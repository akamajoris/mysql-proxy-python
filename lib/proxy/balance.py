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


def idle_failsafe_rw(proxy):
	backend_ndx = 0

	for i, s in enumerate(proxy.globals.backends):
		try:
			conns = s.pool.users[proxy.connection.client.username]
			cur_idle_connections = conns.cur_idle_connections
		except:
			cur_idle_connections = 0
		if cur_idle_connections > 0 and\
				   s.state != proxy.BACKEND_STATE_DOWN and\
				   s.type == proxy.BACKEND_TYPE_RW:
			backend_ndx = i
			break

	return backend_ndx


def idle_ro(proxy):
	max_conns = -1
	max_conns_ndx = 0

	for i, s in enumerate(proxy.globals.backends):
		try:
			conns = s.pool.users[proxy.connection.client.username]
			cur_idle_connections = conns.cur_idle_connections
		except:
			cur_idle_connections = 0

		#- pick a slave which has some idling connections
		if s.type == proxy.BACKEND_TYPE_RO and\
				   s.state != proxy.BACKEND_STATE_DOWN and\
				   cur_idle_connections > 0:
			if max_conns == -1 or s.connected_clients < max_conns:
				max_conns = s.connected_clients
				max_conns_ndx = i

	return max_conns_ndx
