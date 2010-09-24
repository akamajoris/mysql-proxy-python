
import os, sys
sys.path.append(os.environ['PYTHON_LIBPATH'])

import mysql.proto as proto

def connect_server(proxy):
	#-- emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (
			proto.to_challenge_packet({}),
		)
	}
	return proxy.PROXY_SEND_RESULT
