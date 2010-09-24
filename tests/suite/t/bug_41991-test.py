
import os, sys
sys.path.append(os.environ['PYTHON_LIBPATH'])

import mysql.proto as proto

def read_query(proxy, packet):
	#- pass on everything that is not on the initial connection

	if ord(packet[0]) != proxy.COM_QUERY:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK
		}
		return proxy.PROXY_SEND_RESULT

	if packet[1:] == "REFRESH":
		proxy.queries.append(1, chr(7)) #- we don't need the result

		return proxy.PROXY_SEND_QUERY
	else:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_ERR,
			'errmsg' : "(bug_41991-test) >" + packet[1:] + "<"
		}
		return proxy.PROXY_SEND_RESULT
