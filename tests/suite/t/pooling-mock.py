
import os, sys
sys.path.append(os.environ['PYTHON_LIBPATH'])

#--
#- test if connection pooling works
#-
#- by comparing the statement-ids and the connection ids we can 
#- track if the ro-pooling script was reusing a connection
#-

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
		"\000"                #- challenge - part II

#- will be called once after connect

g_conn_id = None

def connect_server(proxy):
	global g_conn_id
	#- the first connection inits the global counter
	#print 'Mock connect_server begin, proxy:', id(proxy)
	if not hasattr(proxy.globals, 'conn_id'):
		proxy.globals.conn_id = 0
	if not hasattr(proxy.globals, 'stmt_id'):
		proxy.globals.stmt_id = 0
	if g_conn_id is None:
		g_conn_id = 0
	print 'Mock connect_server begin, stmt_id=', proxy.globals.stmt_id, ', conn_id=',\
			proxy.globals.conn_id, 'global.conn_id=', g_conn_id
	g_conn_id += 1
	proxy.globals.conn_id = g_conn_id

	#- emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (
			packet_auth(),
		)
	}
	print 'Mock connect_server return, stmt_id=', proxy.globals.stmt_id, ',\
		conn_id=', proxy.globals.conn_id
	return proxy.PROXY_SEND_RESULT

def read_query(proxy, packet):
	if not hasattr(proxy.globals, 'conn_id'):
		proxy.globals.conn_id = 0
	if not hasattr(proxy.globals, 'stmt_id'):
		proxy.globals.stmt_id = 0
	print 'Mock read_query get packet:', packet
	print 'Mock read_query begin, stmt_id=', proxy.globals.stmt_id, ',\
			conn_id=', proxy.globals.conn_id
	if ord(packet[0]) != proxy.COM_QUERY:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK
		}
		print 'Mock read_query return 1, stmt_id=', proxy.globals.stmt_id, ',\
			conn_id=', proxy.globals.conn_id
		return proxy.PROXY_SEND_RESULT

	#- query-counter for this connection
	proxy.globals.stmt_id += 1

	query = packet[1:]
	if query == 'SELECT counter':
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					('conn_id', proxy.MYSQL_TYPE_STRING ),
					('stmt_id', proxy.MYSQL_TYPE_STRING ),
				),
				'rows' : ( ( str(proxy.globals.conn_id), str(proxy.globals.stmt_id)), )
			}
		}
	else:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_ERR,
			'errmsg' : "(pooling-mock) " + query
		}
	print 'Mock read_query return 2, stmt_id=', proxy.globals.stmt_id, ',\
	conn_id=', proxy.globals.conn_id
	return proxy.PROXY_SEND_RESULT
