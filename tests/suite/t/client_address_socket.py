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
# # LICENSE END


def packet_auth(fields = {}):
	return "\x0a" +\
		fields.get('version', "5.0.45-proxy") +\
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
		"\000"                # challenge - part II

def connect_server(proxy):
	print 'connect server'
	# emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : [packet_auth()],
	}
	return proxy.PROXY_SEND_RESULT

# reply with a single field and row containing an indication if we resolved the client's address.
# it should not be NULL!
def read_query(proxy, packet):
	print 'read_query', packet

	if ord(packet[0]) != proxy.COM_QUERY:
		print 'not a query'
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK
		}
		return proxy.PROXY_SEND_RESULT
	query = packet[1:]
	#
    # Uncomment the following three lines if using with MySQL command line.
    # Keep them commented if using inside the test suite
    # counter = counter + 1
    # if counter < 3:
	# 	 return
	if proxy.connection.client.src.address != None:
		client_addr_check = "not-None"
	else:
		client_addr_check = "None"
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_OK,
		'resultset' : {
			'fields' : [['client', proxy.MYSQL_TYPE_STRING]],
			'rows' : [[client_addr_check]],
		}
	}
	#proxy.response.type = proxy.MYSQLD_PACKET_OK
	#proxy.response.resultset = {
	#	'fields' : (
	#		('client', proxy.MYSQL_TYPE_STRING),
	#	),
	#	'rows' : ( ( client_addr_check, ), )
	#}
	print 'now return proxy send result'
	return proxy.PROXY_SEND_RESULT
