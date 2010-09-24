
import os, sys
sys.path.append(os.environ['PYTHON_LIBPATH'])

import mysql.proto as proto

def packet_auth_40():
	return \
		"\x08\x34\x2e\x30\x2e\x32\x38\x2d\x64\x65\x62\x75\x67\x2d\x6c\x6f" +\
		"\x67\000\005\000\000\000\x24\x6a\x6b\x5a\x60\x56\x6b\x3b\000\x2c" +\
		"\20\x08\002\000\000\000\000\000\000\000\000\000\000\000\000\000" +\
		"\000"

def packet_auth_50():
	return proto.to_challenge_packet({})


connects = 0
connect_id = 0

def connect_server(proxy):
	global connects
	global connect_id
	proxy.response.type = proxy.MYSQLD_PACKET_RAW

	if connects == 0:
		proxy.response.packets = ( packet_auth_50(), )
	else:
		proxy.response.packets = ( packet_auth_40(), )

	connect_id = connects
	connects += 1
	print 'Now the connects is:', connects
	return proxy.PROXY_SEND_RESULT


def read_query(proxy, packet):
	global connects
	global connect_id
	if ord(packet[0]) != proxy.COM_QUERY:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK
		}
		return proxy.PROXY_SEND_RESULT

	query = packet[1:]
	if query == "SELECT thread_id()":
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					("thread_id", proxy.MYSQL_TYPE_STRING ),
				),
				'rows' : (
					( connect_id,  ),
				)
			}
		}
	else:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_ERR,
			'errmsg' : "(mysql-40-mock) " + query
		}

	return proxy.PROXY_SEND_RESULT





