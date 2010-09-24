
import os, sys
sys.path.append(os.environ['PYTHON_LIBPATH'])

import mysql.proto as proto

def connect_server(proxy):
	#- emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (
			proto.to_challenge_packet({
				'server_version' : 50120
			}),
		)
	}
	return proxy.PROXY_SEND_RESULT

def read_query(proxy ,packet):
	if ord(packet[0]) != proxy.COM_QUERY:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK
		}
		return proxy.PROXY_SEND_RESULT

	#if packet:sub(2, #("SELECT LENGTH") + 1) == "SELECT LENGTH" then
	if packet[1:].startswith("SELECT LENGTH"):
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					( "length", proxy.MYSQL_TYPE_STRING ),
				),
				'rows' : ( ( len(packet), ),  )
			}
		}
	#elif packet:sub(2, #("SELECT ") + 1) == "SELECT " then
	elif packet[1:].startswith("SELECT "):
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					("length", proxy.MYSQL_TYPE_STRING ),
				),
				'rows' : ( ( packet[1+len("SELECT "):], ), )
			}
		}
	else:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_ERR,
			'errmsg' : "mock doesn't know how to handle query"
		}

	return proxy.PROXY_SEND_RESULT
