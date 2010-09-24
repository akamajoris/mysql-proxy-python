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


print 'begin import'

import proxy.tokenizer as tokenizer

from proxy_utils import get_query_type, get_query_content

print 'Importing'

def read_query(proxy, packet):
	print 'Get a query!'
	if get_query_type(packet) == proxy.COM_QUERY:
		tokens = tokenizer.tokenize(get_query_content(packet))
		for i, token in enumerate(tokens):
			print i, '(', token.token_name, ',', token.text, ')'
