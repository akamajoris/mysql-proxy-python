
import os, sys
sys.path.append(os.environ['PYTHON_LIBPATH'])

import chassis

def read_query(proxy, packet):
	if ord(packet[0]) != proxy.COM_QUERY:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK
		}
		return proxy.PROXY_SEND_RESULT

	if packet[1:] == "SELECT LONG_STRING":
		print 'Get select long string'
		#- return a 16M string
		data_16m = 'x'*(16 * 1024 * 1024 + 1)
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					( "LONG_STRING", proxy.MYSQL_TYPE_STRING ),
				),
				'rows' : ((data_16m, ), )
			}
		}
		return proxy.PROXY_SEND_RESULT
	#elif packet:sub(2, #("SELECT REPLACE") + 1) == "SELECT REPLACE" then
	elif packet[1:].startswith("SELECT REPLACE"):
		#- replace the long query by a small one
		proxy.queries.append(1, chr(3) + 'SELECT \"xxx\"', False)
		return proxy.PROXY_SEND_QUERY
	#elif packet:sub(2, #("SELECT SMALL_QUERY") + 1) == "SELECT SMALL_QUERY" then
	elif packet[1:].startswith("SELECT SMALL_QUERY"):
		#- replace the small query by a long one
		proxy.queries.append(1, chr(3) + "SELECT " + 'x'*(16 * 1024 * 1024 + 1) , False )
		return proxy.PROXY_SEND_QUERY
	elif packet[1:].startswith("SELECT LENGTH"):
		#- forward the LENGTH queries AS IS
		return
	elif packet[1:].startswith("SELECT RESULT"):
		#- pass this query to the result-set handler
		proxy.queries.append(2, packet, True )
		return proxy.PROXY_SEND_QUERY
	elif packet[1:].startswith("SELECT SMALL_RESULT"):
		#- pass this query to the result-set handler
		proxy.queries.append(2, chr(3) + "SELECT " + "x"*(16 * 1024 * 1024 + 1) ,  True )
		return proxy.PROXY_SEND_QUERY
	else:
		#- everything feed through the proxy
		proxy.queries.append(1, packet, False )
		return proxy.PROXY_SEND_QUERY

def read_query_result(proxy, inj):
	if inj.id == 2 :
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					( "result", proxy.MYSQL_TYPE_STRING ),
				),
				'rows' : ( ( "PASSED",  ), )
			}
		}
		return proxy.PROXY_SEND_RESULT
