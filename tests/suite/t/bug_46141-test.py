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
