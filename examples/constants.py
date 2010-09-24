
import sys
#- we need at least 0.5.1
assert proxy.PROXY_VERSION >= 0x00501, "you need at least mysql-proxy 0.5.1 to run this module"

#--
#- read_query() gets the client query before it reaches the server
#-
#- @param packet the mysql-packet sent by client
#-
#- we have several constants defined, e.g.:
#- * _VERSION
#-
#- * proxy.PROXY_VERSION
#- * proxy.COM_*
#- * proxy.MYSQL_FIELD_*
#-

from proxy_utils import get_query_type, get_query_content


def read_query( proxy, packet ):
	if get_query_type(packet) == proxy.COM_QUERY:
		print "get got a Query: " + get_query_content(packet)

		#- proxy.PROXY_VERSION is the proxy version as HEX number
		#- 0x00501 is 0.5.1
		print "we are: " + "%05s" % proxy.PROXY_VERSION
		print "python is: " + sys.version
