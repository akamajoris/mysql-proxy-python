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


def packet_auth(fields = {}):
	return "\x0a" +\
		fields.get("version", "5.0.45-proxy") + \
		"\000" +\
		"\001\000\000\000" +\
		"\x41\x41\x41\x41" +\
		"\x41\x41\x41\x41" +\
		"\000" +\
		"\001\x82" +\
		"\x08" +\
		"\002\000" +\
		"\000" * 13 +\
		"\x41\x41\x41\x41"+\
		"\x41\x41\x41\x41"+\
		"\x41\x41\x41\x41"+\
		"\000"

def connect_server(proxy):
	#- emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (
			packet_auth(),
		)
	}
	return proxy.PROXY_SEND_RESULT

def read_query(proxy, packet):
	if ord(packet[0]) != proxy.COM_QUERY :
		proxy.response = {
		'type' : proxy.MYSQLD_PACKET_OK
	}
		return proxy.PROXY_SEND_RESULT
	query = packet[1:]
	if query == 'SELECT 1, "ADDITION"' :
		proxy.queries.append(1, chr(proxy.COM_QUERY) + 'SELECT 1, "ADDITION", "SECOND ADDITION"')
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					('1', proxy.MYSQL_TYPE_STRING ),
					('ADDITION', proxy.MYSQL_TYPE_STRING ),
					('SECOND ADDITION', proxy.MYSQL_TYPE_STRING )
				),
				'rows' : (
					( '1' , 'ADDITION' , 'SECOND ADDITION' ),
				)
			}
		}
	else:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_ERR,
			'errmsg' : "(chain1a.py) " + query
		}
	return proxy.PROXY_SEND_RESULT
