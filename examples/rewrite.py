

import re
import proxy_utils as utils



def read_query(proxy, packet):
	if utils.get_query_type(packet) == proxy.COM_QUERY:
		query = utils.get_query_content(packet)
		print 'Got a query', query
		cmd = option = None
		cmd_match = re.compile('^\s*(\w+)').match(query)
		if cmd_match:
			cmd = cmd_match.group(1)
			option_match =\
					re.compile('\s+(\w+)').match(query[cmd_match.end(1):])
			if option_match:
				option = option_match.group(1)

		if cmd.lower() == 'ls':
			if option:
				proxy.queries.append(1, chr(proxy.COM_QUERY) +\
						'SHOW TABLES FROM ' + option)
			else:
				proxy.queries.append(1, chr(proxy.COM_QUERY) + 'SHOW TABLES')
			return proxy.PROXY_SEND_QUERY

		elif cmd.lower() == 'who':
			proxy.queries.append(1, chr(proxy.COM_QUERY) + 'SHOW PROCESSLIST')
			return proxy.PROXY_SEND_QUERY

		elif cmd.lower() == 'cd' and option:
			proxy.queries.append(1, chr(proxy.COM_INIT_DB) + option)
			return proxy.PROXY_SEND_QUERY

