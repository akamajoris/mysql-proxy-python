

def read_query(proxy, packet):
	if ord(packet[0]) == proxy.COM_QUERY:
		if packet[1:].startswith("SELECT affected_rows"):
			proxy.response.type = proxy.MYSQLD_PACKET_OK
			proxy.response.resultset = {
				'fields' : (
					( "rows", proxy.MYSQL_TYPE_LONG ),
				),
				'rows' : (
					( proxy.globals.affected_rows, ),
				)
			}

			return proxy.PROXY_SEND_RESULT
		else:
			proxy.queries.append(1, packet)

			return proxy.PROXY_SEND_QUERY

def read_query_result(proxy, inj):
	proxy.globals.affected_rows = inj.resultset.affected_rows
