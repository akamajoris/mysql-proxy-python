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

import chassis
import mysql.proto as proto


def connect_server(proxy):
	#- emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (proto.to_challenge_packet({}), )
	}
	return proxy.PROXY_SEND_RESULT

def read_query(proxy, packet):
	if ord(packet[0]) != proxy.COM_QUERY:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK
		}
		return proxy.PROXY_SEND_RESULT

	query = packet[1:]
	if query == 'SELECT 1':
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					('1', proxy.MYSQL_TYPE_STRING),
				),
				'rows' : ( (1, ), )
			}
		}
	elif query == 'SELECT ':
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_ERR,
			'errmsg' : "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '' at line 1",
			'sqlstate' : "42000",
			'errcode' : 1064
		}
	elif query == 'test_res_blob':
		#- we need a long string, more than 255 chars
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					("300x", proxy.MYSQL_TYPE_BLOB),
				),
				'rows' : (
					( ('x' * 300, ), )
				)
			}
		}
	elif query == 'SELECT row_count(1), bytes()':
		#- we need a long string, more than 255 chars
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					("f1", proxy.MYSQL_TYPE_STRING),
					("f2", proxy.MYSQL_TYPE_STRING),
				),
				'rows' : (
					( "1", "2" ),
					( "1", "2" ),
				)
			}
		}
	elif query == 'INSERT INTO test.t1 VALUES ( 1 )':
		#- we need a long string, more than 255 chars
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'affected_rows' : 2,
			'insert_id' : 10
		}
	elif query == 'SELECT error_msg()':
		#- we need a long string, more than 255 chars
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_ERR,
			'errmsg' : "returning SQL-state 42000 and error-code 1064",
			'sqlstate' : "42000",
			'errcode' : 1064
		}
	elif query == 'SELECT 5.0':
		#- return a empty row
		#-
		proxy.response.type = proxy.MYSQLD_PACKET_RAW
		proxy.response.packets = [
			"\x01",  #- one field
			"\x03def" +   #- catalog
			  "\x00" +    #- db
			  "\x00" +    #- table
			  "\x00" +    #- orig-table
			  "\x011" + #- name
			  "\x00" +    #- orig-name
			  "\x0c" +    #- filler
			  "\x08\x00" + #- charset
			  " \x00\x00\x00" + #- length
			  "\x03" +    #- type
			  "\x02\x00" +  #- flags
			  "\x00" +    #- decimals
			  "\x00\x00",    #- filler

			"\xfe\x00\x00\x02\x00", #- EOF
			"\x011",
			"\xfe\x00\x00\x02\x00"  #- no data EOF
		]
		return proxy.PROXY_SEND_RESULT
	elif query == 'SELECT 4.1':
		#- return a empty row
		#-
		proxy.response.type = proxy.MYSQLD_PACKET_RAW
		proxy.response.packets = (
			"\001",  #-- one field
			"\003def" +   #- catalog
			  "\0" +    #- db 
			  "\0" +    #- table
			  "\0" +    #- orig-table
			  "\0011" + #- name
			  "\0" +    #- orig-name
			  "\f" +    #- filler
			  "\010\0" + #- charset
			  " \0\0\0" + #- length
			  "\003" +    #- type
			  "\002\0" +  #- flags 
			  "\0" +    #- decimals
			  "\0\0",    #- filler

			"\xfe", #- EOF
			"\0011",
			"\xfe\0\0\002\0"  #- no data EOF
		)
		
		return proxy.PROXY_SEND_RESULT

	else:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_ERR,
			'errmsg' : "(resultset-mock) >" + query + "<"
		}
	return proxy.PROXY_SEND_RESULT
