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



import re
import proxy_utils as utils


query_counter = 0


def read_query(proxy, packet):
	if not hasattr(proxy.globals, 'query_counter'):
		proxy.globals.query_counter = 0
	proxy.globals.query_counter += 1
	global query_counter
	query_counter += 1
	query = utils.get_query_content(packet)
	if utils.get_query_type(packet) == proxy.COM_QUERY:
		res = re.split('\s+', query)
		res = filter(lambda x:x.lower().strip(), res)
		if res == ['show', 'query_counter']:
			proxy.response.type = proxy.MYSQLD_PACKET_OK
			proxy.response.resultset = {
				'fields' : [('global_query_counter', proxy.MYSQL_TYPE_LONG),
							('query_counter', proxy.MYSQL_TYPE_LONG)],
				'rows' : [(proxy.globals.query_counter, query_counter)],
			}
			return proxy.PROXY_SEND_RESULT
		elif res == ['show', 'myerror']:
			proxy.response.type = proxy.MYSQLD_PACKET_ERR
			proxy.response.errmsg = 'my first error'
			return proxy.PROXY_SEND_RESULT
