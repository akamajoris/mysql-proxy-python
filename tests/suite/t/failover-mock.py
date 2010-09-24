#--
#- test if failover works
#-
#- * this script is started twice to simulate two backends
#- * one is shutdown in the test with COM_SHUTDOWN
#-

import os, sys, re
sys.path.append(os.environ['PYTHON_LIBPATH'])

import chassis

def packet_auth(fields={}):
	return "\x0a" +\
		fields.get('version', "5.0.45-proxy") +\
		"\x00" +\
		"\x01\x00\x00\x00" +\
		"\x41\x41\x41\x41" +\
		"\x41\x41\x41\x41" +\
		"\x00" +\
		"\x01\x82" +\
		"\x08" +\
		"\x02\x00" +\
		"\x00" * 13 +\
		"\x41\x41\x41\x41"+\
		"\x41\x41\x41\x41"+\
		"\x41\x41\x41\x41"+\
		"\x00"                #- challenge - part II


def check_backend_id(fun):
	def wrapper(*args, **kwds):
		proxy = args[0]
		if not hasattr(proxy.globals, 'backend_id'):
			proxy.globals.backend_id = 0
		return fun(*args, **kwds)
	return wrapper


@check_backend_id
def connect_server(proxy):
	#- emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (
			packet_auth(),
		)
	}
	return proxy.PROXY_SEND_RESULT


#--
#-
@check_backend_id
def read_query(proxy, packet):
	if ord(packet[0]) == proxy.COM_SHUTDOWN:
		#- stop the proxy if we are asked to
		chassis.set_shutdown()
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_RAW,
			'packets' : [ chr(254) ],
		}
		return proxy.PROXY_SEND_RESULT
	elif ord(packet[0]) != proxy.COM_QUERY:
		#- just ACK all non COM_QUERY's
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK
		}
		return proxy.PROXY_SEND_RESULT

	query = packet[1:]
	set_id = re.compile('SET ID (.)').match(query)

	if query == 'GET ID':
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					('id', proxy.MYSQL_TYPE_STRING),
				),
				'rows' : [ [ str(proxy.globals.backend_id)] ]
			}
		}
	elif set_id:
		proxy.globals.backend_id = set_id.group(1)
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : [
					['id', proxy.MYSQL_TYPE_STRING ],
				],
				'rows' : [ [ str(proxy.globals.backend_id) ] ]
			}
		}

	else:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_ERR,
			'errmsg' : "(pooling-mock) " + query
		}
	return proxy.PROXY_SEND_RESULT
