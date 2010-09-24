

import proxy_utils as utils


def read_query(proxy, packet):
	if utils.get_query_type(packet) == proxy.COM_QUERY:
		proxy.queries.append(1, packet, False)
		return proxy.PROXY_SEND_QUERY


def read_query_result(proxy, inj):
	print 'query-time:', inj.query_time/1000, 'ms'
	print 'response-time:', inj.response_time/1000, 'ms'
