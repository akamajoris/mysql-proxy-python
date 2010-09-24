
def packet_auth(fields = {}):
	return "\x0a" +\
		fields.get("version", "5.0.45-proxy") + \
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
		"\000"

def connect_server(proxy):
	#- emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (
			packet_auth(),
		)
	}
	return proxy.PROXY_SEND_RESULT

def read_query(proxy, packet):
	if ord(packet[0]) != proxy.COM_QUERY :
		proxy.response = {
		'type' : proxy.MYSQLD_PACKET_OK
	}
		return proxy.PROXY_SEND_RESULT
	query = packet[1:]
	if query == 'SELECT 1, "ADDITION"' :
		proxy.queries.append(1, chr(proxy.COM_QUERY) + 'SELECT 1, "ADDITION", "SECOND ADDITION"')
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					('1', proxy.MYSQL_TYPE_STRING ),
					('ADDITION', proxy.MYSQL_TYPE_STRING ),
					('SECOND ADDITION', proxy.MYSQL_TYPE_STRING )
				),
				'rows' : (
					( '1' , 'ADDITION' , 'SECOND ADDITION' ),
				)
			}
		}
	else:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_ERR,
			'errmsg' : "(chain1a.py) " + query
		}
	return proxy.PROXY_SEND_RESULT
