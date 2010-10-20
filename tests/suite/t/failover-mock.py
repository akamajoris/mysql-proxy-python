# LICENSE BEGIN
#
# Copyright (c) 2010 Ysj.Ray
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
## LICENSE END

#--
#- test if failover works
#-
#- * this script is started twice to simulate two backends
#- * one is shutdown in the test with COM_SHUTDOWN
#-

import os, sys, re
sys.path.append(os.environ['PYTHON_LIBPATH'])

import chassis

def packet_auth(fields={}):
	return "\x0a" +\
		fields.get('version', "5.0.45-proxy") +\
		"\x00" +\
		"\x01\x00\x00\x00" +\
		"\x41\x41\x41\x41" +\
		"\x41\x41\x41\x41" +\
		"\x00" +\
		"\x01\x82" +\
		"\x08" +\
		"\x02\x00" +\
		"\x00" * 13 +\
		"\x41\x41\x41\x41"+\
		"\x41\x41\x41\x41"+\
		"\x41\x41\x41\x41"+\
		"\x00"                #- challenge - part II


def check_backend_id(fun):
	def wrapper(*args, **kwds):
		proxy = args[0]
		if not hasattr(proxy.globals, 'backend_id'):
			proxy.globals.backend_id = 0
		return fun(*args, **kwds)
	return wrapper


@check_backend_id
def connect_server(proxy):
	print 'mock connect server'
	#- emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (
			packet_auth(),
		)
	}
	return proxy.PROXY_SEND_RESULT


#--
#-
@check_backend_id
def read_query(proxy, packet):
	print 'mock read query:%d, <%s>' % (ord(packet[0]), packet[1:])
	if ord(packet[0]) == proxy.COM_SHUTDOWN:
		#- stop the proxy if we are asked to
		chassis.set_shutdown()
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_RAW,
			'packets' : [ chr(254) ],
		}
		return proxy.PROXY_SEND_RESULT
	elif ord(packet[0]) != proxy.COM_QUERY:
		#- just ACK all non COM_QUERY's
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK
		}
		return proxy.PROXY_SEND_RESULT

	query = packet[1:]
	set_id = re.compile('SET ID (.)').match(query)

	if query == 'GET ID':
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					('id', proxy.MYSQL_TYPE_STRING),
				),
				'rows' : [ [ str(proxy.globals.backend_id)] ]
			}
		}
	elif set_id:
		proxy.globals.backend_id = set_id.group(1)
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : [
					['id', proxy.MYSQL_TYPE_STRING ],
				],
				'rows' : [ [ str(proxy.globals.backend_id) ] ]
			}
		}

	else:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_ERR,
			'errmsg' : "(pooling-mock) " + query
		}
	return proxy.PROXY_SEND_RESULT
