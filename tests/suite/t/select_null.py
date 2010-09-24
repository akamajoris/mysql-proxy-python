
def packet_auth(fields = {}):
	packet = "\x0a" +\
		fields.get('version', "5.0.45-proxy") +\
		"\x00" +\
		"\x01\x00\x00\x00" +\
		"\x41\x41\x41\x41" +\
		"\x41\x41\x41\x41" +\
		"\x00" +\
		"\x01\x82" +\
		"\x08" +\
		"\x02\x00" +\
		"\x00"*13 +\
		"\x41\x41\x41\x41"+\
		"\x41\x41\x41\x41"+\
		"\x41\x41\x41\x41"+\
		"\x00"
	return packet

def connect_server(proxy):
	#- emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (
			packet_auth(),
		)
	}
	return proxy.PROXY_SEND_RESULT

def read_query(proxy, packet ):
	if ord(packet[0]) != proxy.COM_QUERY:
		proxy.response = { 'type' : proxy.MYSQLD_PACKET_OK }
		return proxy.PROXY_SEND_RESULT

	#if packet:sub(2) == "SELECT NULL" then
	if packet[1:] == "SELECT NULL":
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : [ ["NULL", proxy.MYSQL_TYPE_STRING]],
				'rows' : [
					[ 'NULL']
				]
			}
		}

	return proxy.PROXY_SEND_RESULT
