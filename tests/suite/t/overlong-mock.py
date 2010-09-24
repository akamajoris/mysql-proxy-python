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

def connect_server(proxy):
	#- emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (
			proto.to_challenge_packet({
				'server_version' : 50120
			}),
		)
	}
	return proxy.PROXY_SEND_RESULT

def read_query(proxy ,packet):
	if ord(packet[0]) != proxy.COM_QUERY:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK
		}
		return proxy.PROXY_SEND_RESULT

	#if packet:sub(2, #("SELECT LENGTH") + 1) == "SELECT LENGTH" then
	if packet[1:].startswith("SELECT LENGTH"):
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					( "length", proxy.MYSQL_TYPE_STRING ),
				),
				'rows' : ( ( len(packet), ),  )
			}
		}
	#elif packet:sub(2, #("SELECT ") + 1) == "SELECT " then
	elif packet[1:].startswith("SELECT "):
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					("length", proxy.MYSQL_TYPE_STRING ),
				),
				'rows' : ( ( packet[1+len("SELECT "):], ), )
			}
		}
	else:
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_ERR,
			'errmsg' : "mock doesn't know how to handle query"
		}

	return proxy.PROXY_SEND_RESULT
