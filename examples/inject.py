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
    query = get_query_content(packet)
    if get_query_type(packet) == proxy.COM_QUERY:
        print 'Got a normal query:', get_query_content(packet)
        proxy.queries.append(1, packet)
        proxy.queries.append(2, chr(proxy.COM_QUERY) + 'select now()', True)
        return proxy.PROXY_SEND_QUERY


def read_query_result(proxy, inj):
    print 'injected result-set id:', inj.id
    if inj.id == 2:
        for r in inj.resultset.rows:
            print 'injected query returned:', r[0]
        return proxy.PROXY_IGNORE_RESULT
