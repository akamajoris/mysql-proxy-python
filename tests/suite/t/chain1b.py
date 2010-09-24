
def read_query(proxy, packet):
	if ord(packet[0]) != proxy.COM_QUERY:
		return
	query = packet[1:]
	if query == 'SELECT 1':
		proxy.queries.append(1, chr(proxy.COM_QUERY) + 'SELECT 1, "ADDITION"')
		return proxy.PROXY_SEND_QUERY

def read_query_result(proxy, inj):
	pass
