
#--
#- Bug #46141 
#-
#-   .prepend() does handle the 3rd optional parameter
#-
#- which leads to a not-working read_query_result() for queries that
#- got prepended to the query-queue
#-
def read_query(proxy, packet):
	#- pass on everything that is not on the initial connection

	if ord(packet[0]) != proxy.COM_QUERY :
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK
		}
		return proxy.PROXY_SEND_RESULT

	if packet[1:] == "SELECT 1" :
		proxy.queries.prepend(1, packet, 1)

		return proxy.PROXY_SEND_QUERY
	else:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_ERR,
			'errmsg' : "(bug_41991-test) >" + packet[1:] + "<"
		}
		return proxy.PROXY_SEND_RESULT


def read_query_result(proxy, inj):
	if inj.id == 1 :
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					( "1", proxy.MYSQL_TYPE_STRING ),
				),
				'rows' : (
					( "2", ),
				)
			}
		}
		return proxy.PROXY_SEND_RESULT
