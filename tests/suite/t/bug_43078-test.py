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


def read_query(proxy, packet ):
	if ord(packet[0]) != proxy.COM_QUERY:
		proxy.response = { 'type' : proxy.MYSQLD_PACKET_OK }
		return proxy.PROXY_SEND_RESULT

	proxy.queries.append(1, packet, True )

	return proxy.PROXY_SEND_QUERY

def read_query_result(proxy, inj):
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_OK,
		'resultset' : {
			'fields' : (
				("fields", proxy.MYSQL_TYPE_STRING),
			),
			'rows' : ( ( len(inj.resultset.fields), ), )
		}
	}
	return proxy.PROXY_SEND_RESULT
