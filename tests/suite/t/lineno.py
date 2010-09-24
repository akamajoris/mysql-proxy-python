
import os, sys
sys.path.append(os.environ['PYTHON_LIBPATH'])
import traceback

import mysql.proto as proto

def connect_server(proxy):
	#- emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (
			proto.to_challenge_packet({}),
		)
	}
	return proxy.PROXY_SEND_RESULT


def read_query(proxy, packet):
	if ord(packet[0]) != proxy.COM_QUERY :
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
		}
		return proxy.PROXY_SEND_RESULT

	if packet[1:] == "SELECT backtrace" :
		try:
			raise Exception("test")
		except:
			pass
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					( "backtrace", proxy.MYSQL_TYPE_STRING ),
				),
				'rows' : (
					( traceback.format_exc(), ),
				)
			}
		}
	else:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_ERR,
			'errmsg' : packet[1:]
		}

	return proxy.PROXY_SEND_RESULT

