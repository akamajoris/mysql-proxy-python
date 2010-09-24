
import os, sys
sys.path.append(os.environ['PYTHON_LIBPATH'])

import chassis
#--
#- reply with a single field and row containing an indication if we resolved the client's address.
#-
#- some fields are not preditable, so we only say "nil" or "not nil"
def read_query(proxy, packet ):
	if ord(packet[0]) != proxy.COM_QUERY :
		proxy.response = { 'type' : proxy.MYSQLD_PACKET_OK }
		return proxy.PROXY_SEND_RESULT

	query = packet[1:]

	print 'get query:', query
	value = errmsg = None
	exec(query)

	print 'get result:', value, errmsg

	if not value:
		chassis.log("critical", query)
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_ERR,
			'errmsg' : errmsg
		}
	else:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					("value", proxy.MYSQL_TYPE_STRING),
				),
				'rows' : [[value]]
			}
		}
	return proxy.PROXY_SEND_RESULT
