
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
		"\x41\x41\x41\x41" +\
		"\x41\x41\x41\x41" +\
		"\x41\x41\x41\x41" +\
		"\000"                #- challenge - part II

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

	import re
	m = re.search('^\s*select\s+error\s+(\d+)\s+(\w+)\s+"(.*)"', packet[1:].lower())
	if m:
		err_code, sql_state, err_msg = m.groups()
	else:
		err_code, sql_state, err_msg = None, None, None
	print '<%s>, <%s>, <%s>' % (err_code, sql_state, err_msg)

	if err_code and sql_state:
		try:
			proxy.response = {
				'type'     : proxy.MYSQLD_PACKET_ERR,
				'errmsg'   : err_msg,
				'errcode'  : int(err_code),
				'sqlstate' : sql_state
			}
			return proxy.PROXY_SEND_RESULT
		except:
			pass
