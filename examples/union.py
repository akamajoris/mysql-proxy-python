


from proxy_utils import get_query_type, get_query_content


def read_query(proxy, packet):
	if get_query_type(packet) != proxy.COM_QUERY:
		print 'Not a query, return'
		return
	print 'Get query:', packet
	query = get_query_content(packet)
	if query[:6].lower() == 'select' and not 'version_comment' in query:
		proxy.queries.append(2, packet, True)
		proxy.queries.append(1, packet, True)
		return proxy.PROXY_SEND_QUERY

res = []

def read_query_result(proxy, inj):
	if inj.id == 1:
		return proxy.PROXY_IGNORE_RESULT
	if inj.id == 2:
		global res
		try:
			for row in inj.resultset.rows:
				res.append(row)
		except:
			pass

		fields = []
		try:
			for f in inj.resultset.fields:
				fields.append((f.name, f.type))
		except:
			pass

		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'rows' : res,
				'fields' : fields,
			}
		}

		return proxy.PROXY_SEND_RESULT
