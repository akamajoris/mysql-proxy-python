# LICENSE BEGIN
#
# Copyright (c) 2010 Ysj.Ray
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
## LICENSE END


import os, sys
sys.path.append(os.environ['PYTHON_LIBPATH'])


import mysql.proto as proto


my_lovely_packet = None

def read_query(proxy, packet):
	proxy.queries.append(1, packet, True )

	global my_lovely_packet
	my_lovely_packet = packet

	return proxy.PROXY_SEND_QUERY

def read_query_result(proxy, inj):
	assert(inj)
	assert(inj.id == 1) # the id we assigned above
	assert(inj.query == my_lovely_packet) # the id we assigned above

	assert(inj.query_time >= 0)
	assert(inj.response_time >= 0)

	res = inj.resultset
	status = res.query_status

	assert(proxy.MYSQLD_PACKET_OK == 0)
	assert(proxy.MYSQLD_PACKET_ERR == 255)

	if status == proxy.MYSQLD_PACKET_OK:
		if inj.query == chr(proxy.COM_QUERY) + "INSERT INTO test.t1 VALUES ( 1 )":
			# convert a OK packet with affected rows into a resultset
			affected_rows = res.affected_rows
			insert_id     = res.insert_id

			proxy.response.type = proxy.MYSQLD_PACKET_OK
			fields = [("affected_rows", proxy.MYSQL_TYPE_LONG), ("insert_id",\
				proxy.MYSQL_TYPE_LONG)]
			rows = [(affected_rows, insert_id)]
			proxy.response.resultset = {'fields' : fields, 'rows' : rows}
			return proxy.PROXY_SEND_RESULT

		elif inj.query == chr(proxy.COM_QUERY) + "SELECT row_count(1), bytes()":
			# convert a OK packet with affected rows into a resultset
			assert(res.affected_rows is None)
			proxy.response.type = proxy.MYSQLD_PACKET_OK
			fields = [("row_count", proxy.MYSQL_TYPE_LONG), ("bytes",\
				proxy.MYSQL_TYPE_LONG)]
			rows = [(res.row_count, res.bytes)]
			proxy.response.resultset = {'fields' : fields, 'rows' : rows}
			return proxy.PROXY_SEND_RESULT

		elif inj.query == chr(proxy.COM_QUERY) + "SELECT 5.0":
			# test if we decode a 5.0 resultset nicely
			assert(res.affected_rows == None)

			proxy.response.type = proxy.MYSQLD_PACKET_OK
			fields = [("row_count", proxy.MYSQL_TYPE_LONG), ("bytes",\
				proxy.MYSQL_TYPE_LONG)]
			rows = [(res.row_count, res.bytes)]
			proxy.response.resultset = {'fields' : fields, 'rows' : rows}
			return proxy.PROXY_SEND_RESULT

		elif inj.query == chr(proxy.COM_QUERY) + "SELECT 4.1":
			# test if we decode a 4.1 resultset too (shorter EOF packets)
			assert(res.affected_rows == None)

			proxy.response.type = proxy.MYSQLD_PACKET_OK
			fields = [("row_count", proxy.MYSQL_TYPE_LONG), ("bytes",\
				proxy.MYSQL_TYPE_LONG)]
			rows = [(res.row_count, res.bytes)]
			proxy.response.resultset = {'fields' : fields, 'rows' : rows}
			return proxy.PROXY_SEND_RESULT

	elif status == proxy.MYSQLD_PACKET_ERR:
		if inj.query == chr(proxy.COM_QUERY) + "SELECT error_msg()":
			# convert a OK packet with affected rows into a resultset
			assert(res.raw)
			err = proto.from_err_packet(res.raw)

			proxy.response = {
				'type' : proxy.MYSQLD_PACKET_OK,
				'resultset' : {
					'fields' : (
						( "errcode",
						  proxy.MYSQL_TYPE_STRING ),
						( "errmsg",
						  proxy.MYSQL_TYPE_STRING ),
						( "sqlstate",
						  proxy.MYSQL_TYPE_STRING ),
					),
					'rows' : (
						(err.errcode, err.errmsg, err.sqlstate),
					)
				}
			}
			return proxy.PROXY_SEND_RESULT

	else:
		print "res.query_status is %d, expected %d or %d" % (res.query_status,\
			proxy.MYSQLD_PACKET_OK, proxy.MYSQLD_PACKET_ERR)
