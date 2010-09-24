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
#- a flexible statement based load balancer with connection pooling
#-
#- * build a connection pool of min_idle_connections for each back and maintain
#-   its size
#- *
#-
#-

import proxy.commands as commands
import proxy.tokenizer as tokenizer
import proxy.balance as lb
import proxy.auto_config as auto_config


class rwsplit_config(object):
	def __init__(self, value=None):
		if type(value) == dict:
			for k, v in value.items():
				setattr(self, k, v)


def check_rwsplit_config(fun):
	# Here the first element of args must be proxy object.
	def wrapper(*args, **kwds):
		proxy = args[0]
		if not hasattr(proxy.globals.config, 'rwsplit'):
			proxy.globals.config.rwsplit = rwsplit_config({
				'min_idle_connections' : 4,
				'max_idle_connections' : 8,
				'is_debug' : False
			})
		return fun(*args, **kwds)
	return wrapper


#--
#- read/write splitting ss all non-transactional SELECTs to the slaves
#-
#- is_in_transaction tracks the state of the transactions

#- if this was a SELECT SQL_CALC_FOUND_ROWS +. stay on the same connections

#--
#- get a connection to a back
#-
#- as long as we don't have enough connections in the pool, create new connections
#-

@check_rwsplit_config
def connect_server(proxy):
	proxy.globals.is_in_transaction = False
	proxy.globals.is_in_select_calc_found_rows = False
	is_debug = proxy.globals.config.rwsplit.is_debug
	#- make sure that we connect to each back at least ones to 
	#- keep the connections to the servers alive
	#-
	#- on read_query we can switch the backs again to another backend

	if is_debug :
		print
		print "[connect_server] " + proxy.connection.client.src.name


	rw_ndx = 0

	#- init all backs
	for i, s in enumerate(proxy.globals.backends):
		pool     = s.pool #- we don't have a username yet, try to find a connections which is idling
		try:
			cur_idle = pool.users[""].cur_idle_connections
		except:
			cur_idle = 0

		pool.min_idle_connections = proxy.globals.config.rwsplit.min_idle_connections
		pool.max_idle_connections = proxy.globals.config.rwsplit.max_idle_connections
		if is_debug :
			print "  ["+ str(i) +"].connected_clients = " + str(s.connected_clients)
			print "  ["+ str(i) +"].pool.cur_idle     = " + str(cur_idle)
			print "  ["+ str(i) +"].pool.max_idle     = " + str(pool.max_idle_connections)
			print "  ["+ str(i) +"].pool.min_idle     = " + str(pool.min_idle_connections)
			print "  ["+ str(i) +"].type = " + str(s.type)
			print "  ["+ str(i) +"].state = " + str(s.state)

		#- prefer connections to the master
		if s.type == proxy.BACKEND_TYPE_RW and\
		   s.state != proxy.BACKEND_STATE_DOWN and\
		   cur_idle < pool.min_idle_connections :
			proxy.connection.backend_ndx = i
			break
		elif s.type == proxy.BACKEND_TYPE_RO and\
		       s.state != proxy.BACKEND_STATE_DOWN and\
		       cur_idle < pool.min_idle_connections :
			proxy.connection.backend_ndx = i
			break
		elif s.type == proxy.BACKEND_TYPE_RW and\
		       s.state != proxy.BACKEND_STATE_DOWN and\
		       rw_ndx == 0 :
			rw_ndx = i

	if proxy.connection.backend_ndx == 0 :
		if is_debug :
			print("  [" + rw_ndx + "] taking master as default")
		proxy.connection.backend_ndx = rw_ndx

	#- pick a random back
	#-
	#- we someone have to skip DOWN backs

	#- ok, did we got a back ?

	if proxy.connection.server :
		if is_debug :
			print "  using pooled connection from: " + proxy.connection.backend_ndx

		#- stay with it
		return proxy.PROXY_IGNORE_RESULT

	if is_debug :
		print("  [" + proxy.connection.backend_ndx + "] idle-conns below min-idle")

	#- open a new connection


#--
#- put the successfully authed connection into the connection pool
#-
#- @param auth the context information for the auth
#-
#- auth.packet is the packet
@check_rwsplit_config
def read_auth_result( proxy, auth ):
	is_debug = proxy.globals.config.rwsplit.is_debug
	if is_debug :
		print "[read_auth_result] " + proxy.connection.client.src.name
	if ord((auth.packet)[0]) == proxy.MYSQLD_PACKET_OK :
		#- auth was fine, disconnect from the server
		proxy.connection.backend_ndx = 0
	elif ord((auth.packet)[0]) == proxy.MYSQLD_PACKET_EOF :
		#- we received either a
		#-
		#- * MYSQLD_PACKET_ERR and the auth failed or
		#- * MYSQLD_PACKET_EOF which means a OLD PASSWORD (4.0) was sent
		print "(read_auth_result) +. not ok yet"
	elif ord((auth.packet)[0]) == proxy.MYSQLD_PACKET_ERR :
		#- auth failed
		pass


#--
#- read/write splitting
@check_rwsplit_config
def read_query(proxy, packet):
	is_debug = proxy.globals.config.rwsplit.is_debug
	cmd      = commands.parse(packet)
	c        = proxy.connection.client

	r = auto_config.handle(cmd, proxy)
	if r : return r

	tokens = None
	#norm_query

	#- looks like we have to forward this statement to a back
	if is_debug :
		print "[read_query] " + proxy.connection.client.src.name
		print "  current back   = " + proxy.connection.backend_ndx
		print "  client default db = " + c.default_db
		print "  client username   = " + c.username
		if cmd.type == proxy.COM_QUERY :
			print "  query             = "        + cmd.query

	if cmd.type == proxy.COM_QUIT :
		#- don't s COM_QUIT to the backend. We manage the connection
		#- in all aspects.
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
		}
		if is_debug :
			print("  (QUIT) current back   = " + proxy.connection.backend_ndx)

		return proxy.PROXY_SEND_RESULT

	proxy.queries.append(1, packet, True )

	#- read/write splitting
	#-
	#- s all non-transactional SELECTs to a slave
	if not proxy.globals.is_in_transaction and cmd.type == proxy.COM_QUERY :
		tokens = tokens or tokenizer.tokenize(cmd.query)

		stmt = tokenizer.first_stmt_token(tokens)

		if stmt.token_name == "TK_SQL_SELECT" :
			proxy.globals.is_in_select_calc_found_rows = False
			is_insert_id = False

			for token in tokens:
				#- SQL_CALC_FOUND_ROWS + FOUND_ROWS() have to be executed
				#- on the same connection
				#- print("token: " + token.token_name)
				#- print("  val: " + token.text)
				if not proxy.globals.is_in_select_calc_found_rows and \
						token.token_name == "TK_SQL_SQL_CALC_FOUND_ROWS" :
					proxy.globals.is_in_select_calc_found_rows = True
				elif not is_insert_id and token.token_name == "TK_LITERAL" :
					utext = token.text.upper()

					if utext in ("LAST_INSERT_ID", "@@INSERT_ID"):
						is_insert_id = True

				#- we found the two special token, we can't find more
				if is_insert_id and proxy.globals.is_in_select_calc_found_rows :
					break

			#- if we ask for the last-insert-id we have to ask it on the original
			#- connection
			if not is_insert_id :
				backend_ndx = lb.idle_ro(proxy)

				if backend_ndx > 0 :
					proxy.connection.backend_ndx = backend_ndx
			else:
				print "   found a SELECT LAST_INSERT_ID(), staying on the same back"

	#- no back selected yet, pick a master
	if proxy.connection.backend_ndx == 0 :
		#- we don't have a back right now
		#-
		#- let's pick a master as a good default
		#-
		proxy.connection.backend_ndx = lb.idle_failsafe_rw(proxy)

	#- by now we should have a back
	#-
	#- in case the master is down, we have to close the client connections
	#- otherwise we can go on
	if proxy.connection.backend_ndx == 0 :
		return proxy.PROXY_SEND_QUERY

	s = proxy.connection.server

	#- if client and server db don't match, adjust the server-side
	#-
	#- skip it if we s a INIT_DB anyway
	if cmd.type != proxy.COM_INIT_DB and\
	   c.default_db and c.default_db != s.default_db :
		print "    server default db: " + s.default_db
		print "    client default db: " + c.default_db
		print "    syncronizing"
		proxy.queries.prepend(2, chr(proxy.COM_INIT_DB) + c.default_db, True )

	#- s to master
	if is_debug :
		if proxy.connection.backend_ndx > 0 :
			b = proxy.globals.backs[proxy.connection.backend_ndx]
			print "  sing to backend : " + b.dst.name
			print "    is_slave         : " + str(b.type == proxy.BACKEND_TYPE_RO)
			print "    server default db: " + s.default_db
			print "    server username  : " + s.username
		print "    in_trans        : " + str(proxy.globals.is_in_transaction)
		print "    in_calc_found   : " + str(proxy.globals.is_in_select_calc_found_rows)
		print "    COM_QUERY       : " + str(cmd.type == proxy.COM_QUERY)

	return proxy.PROXY_SEND_QUERY


#--
#- as long as we are in a transaction keep the connection
#- otherwise release it so another client can use it
@check_rwsplit_config
def read_query_result(proxy, inj ):
	is_debug = proxy.globals.config.rwsplit.is_debug
	res      = inj.resultset
  	flags    = res.flags

	if inj.id != 1 :
		#- ignore the result of the USE <default_db>
		#- the DB might not exist on the back, what do do ?
		#-
		if inj.id == 2 :
			#- the injected INIT_DB failed as the slave doesn't have this DB
			#- or doesn't have permissions to read from it
			if res.query_status == proxy.MYSQLD_PACKET_ERR :
				proxy.queries.reset()

				proxy.response = {
					'type' : proxy.MYSQLD_PACKET_ERR,
					'errmsg' : "can't change DB "+ proxy.connection.client.default_db +
						" to on slave " + proxy.globals.backs[proxy.connection.backend_ndx].dst.name
				}

				return proxy.PROXY_SEND_RESULT

		return proxy.PROXY_IGNORE_RESULT

	proxy.globals.is_in_transaction = flags.in_trans
	have_last_insert_id = (res.insert_id and (res.insert_id > 0))

	if not proxy.globals.is_in_transaction and\
	   not proxy.globals.is_in_select_calc_found_rows and\
	   not have_last_insert_id :
		#- release the back
		proxy.connection.backend_ndx = 0
	elif is_debug :
		print("(read_query_result) staying on the same back")
		print("    in_trans        : " + str(proxy.globals.is_in_transaction))
		print("    in_calc_found   : " + str(proxy.globals.is_in_select_calc_found_rows))
		print("    have_insert_id  : " + str(have_last_insert_id))


#--
#- close the connections if we have enough connections in the pool
#-
#- @return nil - close connection
#-         IGNORE_RESULT - store connection in the pool
@check_rwsplit_config
def disconnect_client(proxy):
	is_debug = proxy.globals.config.rwsplit.is_debug
	if is_debug :
		print("[disconnect_client] " + proxy.connection.client.src.name)

	#- make sure we are disconnection from the connection
	#- to move the connection into the pool
	proxy.connection.backend_ndx = 0


