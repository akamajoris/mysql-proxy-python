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



import proxy_utils as utils



def read_query(proxy, packet):
	if utils.get_query_type(packet) == proxy.COM_QUERY:
		proxy.queries.append(1, packet, True)
		return proxy.PROXY_SEND_QUERY


def read_query_result(proxy, inj):
	if inj.id == 1:
		res = inj.resultset
		if res.warning_count > 0:
			print 'Query had warnings:', utils.get_query_content(inj.query)
			proxy.queries.append(2, chr(proxy.COM_QUERY) + 'SHOW WARNINGS', True)
	elif inj.id == 2:
		for row in inj.resultset.rows:
			print 'warning: [%s] [%s]' % (row[1], row[0])
		return proxy.PROXY_IGNORE_RESULT
