

import proxy_utils as utils



def read_query(proxy, packet):
	if utils.get_query_type(packet) == proxy.COM_QUERY:
		proxy.queries.append(1, packet, True)
		return proxy.PROXY_SEND_QUERY


def read_query_result(proxy, inj):
	if inj.id == 1:
		res = inj.resultset
		if res.warning_count > 0:
			print 'Query had warnings:', utils.get_query_content(inj.query)
			proxy.queries.append(2, chr(proxy.COM_QUERY) + 'SHOW WARNINGS', True)
	elif inj.id == 2:
		for row in inj.resultset.rows:
			print 'warning: [%s] [%s]' % (row[1], row[0])
		return proxy.PROXY_IGNORE_RESULT
