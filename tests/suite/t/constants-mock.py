
import os, sys
sys.path.append(os.environ['PYTHON_LIBPATH'])

import mysql.proto as proto

#--
#- if the assert()ions in -test.py fail, the default behaviour of the proxy
#- will jump in and we will forward the query to the backend. That's us. 
#-
#- We will answer the query. Our answer is "failed" 

def connect_server(proxy):
	#- emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (
			proto.to_challenge_packet({
				'server_version' : 50114
			}),
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
		'type' : proxy.MYSQLD_PACKET_OK,
		'resultset' : {
			'fields' : (
				( "Result", proxy.MYSQL_TYPE_STRING ),
			),
			'rows' : ( ( "failed", ),  )
		}
	}

	return proxy.PROXY_SEND_RESULT

