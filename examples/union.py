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




from proxy_utils import get_query_type, get_query_content


def read_query(proxy, packet):
	if get_query_type(packet) != proxy.COM_QUERY:
		print 'Not a query, return'
		return
	print 'Get query:', packet
	query = get_query_content(packet)
	if query[:6].lower() == 'select' and not 'version_comment' in query:
		proxy.queries.append(2, packet, True)
		proxy.queries.append(1, packet, True)
		return proxy.PROXY_SEND_QUERY

res = []

def read_query_result(proxy, inj):
	if inj.id == 1:
		return proxy.PROXY_IGNORE_RESULT
	if inj.id == 2:
		global res
		try:
			for row in inj.resultset.rows:
				res.append(row)
		except:
			pass

		fields = []
		try:
			for f in inj.resultset.fields:
				fields.append((f.name, f.type))
		except:
			pass

		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'rows' : res,
				'fields' : fields,
			}
		}

		return proxy.PROXY_SEND_RESULT
