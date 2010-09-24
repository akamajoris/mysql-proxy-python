

import proxy_utils as utils



def read_query(proxy, packet):
	if utils.get_query_type(packet) == proxy.COM_QUERY:
		print 'Got a query', utils.get_query_content(packet)
