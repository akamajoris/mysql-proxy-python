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



import mysql.password as password
import mysql.proto as proto


map_auth = {
	'replace' : {
		'password' : 'me',
		'new_user' : 'root',
		'new_password' : 'secret',
	}
}


def read_auth(proxy):
	c = proxy.connection.client
	s = proxy.connection.server
	print 'for challange %s the client sent %s' % (s.scramble_buffer,\
			c.scrambled_password)
	if c.username in map_auth and\
			password.check(s.scramble_buffer, c.scrambled_password,
				password.hash(password.hash(map_auth[c.username]['password']))):
		proxy.queries.append(1, proto.to_response_packet({
			'username' : map_auth[c.username]['new_user'],
			'response' : password.scramble(s.scramble_buffer,
				password.hash(map_auth[c.username]['new_password'])),
			'charset' : 8,
			'database' : c.default_db,
			'max_packet_size' : 1 * 1024 * 1024,
		}))

		return proxy.PROXY_SEND_QUERY
