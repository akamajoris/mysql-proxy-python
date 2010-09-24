

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
