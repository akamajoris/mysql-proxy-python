
def read_query(proxy, packet ):
	if ord(packet[0]) != proxy.COM_QUERY:
		proxy.response = { 'type' : proxy.MYSQLD_PACKET_OK }
		return proxy.PROXY_SEND_RESULT

	proxy.queries.append(1, packet, True )

	return proxy.PROXY_SEND_QUERY

def read_query_result(proxy, inj):
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_OK,
		'resultset' : {
			'fields' : (
				("fields", proxy.MYSQL_TYPE_STRING),
			),
			'rows' : ( ( len(inj.resultset.fields), ), )
		}
	}
	return proxy.PROXY_SEND_RESULT
