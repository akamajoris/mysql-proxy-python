
import re
import os, sys
sys.path.append(os.environ['PYTHON_LIBPATH'])

import mysql.proto as proto

def connect_server(proxy):
	#- emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (
			proto.to_challenge_packet({}),
		)
	}
	return proxy.PROXY_SEND_RESULT

def read_query(proxy, packet):
	if ord(packet[0]) != proxy.COM_QUERY:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK
		}
		return proxy.PROXY_SEND_RESULT

	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_OK,
		'resultset' : {
			'fields' : ( ),
			'rows' : ( ),
		}
	}

	print 'packet:', packet[1:]
	m = re.compile("SELECT (\d+) fields")
	fields_cnt = m.match(packet[1:]).group(1)
	#fields = packet[1:]:match("SELECT (%d+) fields")

	fields_cnt = int(fields_cnt) or 1 #- default to 1

	#for i = 1, fields do
	fields = []
	row = []
	for i in xrange(fields_cnt):
		#proxy.response.resultset.fields[i] = ( str(i), proxy.MYSQL_TYPE_STRING )
		fields.append((str(i), proxy.MYSQL_TYPE_STRING))
		#proxy.response.resultset.rows[1][i] = "1"
		row.append("i")
	proxy.response.resultset.fields = fields
	proxy.response.resultset.rows = (row, )

	return proxy.PROXY_SEND_RESULT
