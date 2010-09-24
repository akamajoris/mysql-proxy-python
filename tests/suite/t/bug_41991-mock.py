
import os, sys
sys.path.append(os.environ['PYTHON_LIBPATH'])

import mysql.proto as proto

def connect_server(proxy):
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (
			proto.to_challenge_packet({}),
		)
	}

	return proxy.PROXY_SEND_RESULT

def read_query(proxy, packet):
	if ord(packet[0]) != proxy.COM_QUERY:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK
		}
		return proxy.PROXY_SEND_RESULT

	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_ERR,
		'errmsg' : "(bug_41991-mock) >" + packet[1:] + "<"
	}
	return proxy.PROXY_SEND_RESULT
