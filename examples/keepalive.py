#-[[



#-]]

#--
#- a flexible statement based load balancer with connection pooling
#-
#- * build a connection pool of min_idle_connections for each backend and
#-   maintain its size
#- * reusing a server-side connection when it is idling
#-

#-- config
#-
#- connection pool
min_idle_connections = 4
max_idle_connections = 8

#- debug
is_debug = True

#-- end of config

#--
#- read/write splitting sends all non-transactional SELECTs to the slaves
#-
#- is_in_transaction tracks the state of the transactions
#is_in_transaction = 0

#--
#- get a connection to a backend
#-
#- as long as we don't have enough connections in the pool, create new connections
#-
def connect_server(proxy):
	#- make sure that we connect to each backend at least ones to
	#- keep the connections to the servers alive
	#-
	#- on read_query we can switch the backends again to another backend

	if is_debug:
		print
		print "[connect_server] "

	least_idle_conns_ndx = -1
	#least_idle_conns = 0

	for i, s in enumerate(proxy.globals.backends):
		pool = s.pool #- we don't have a username yet, try to find a connections which is idling
		try:
			cur_idle = pool.users[""].cur_idle_connections
		except:
			cur_idle = 0

		if is_debug :
			print "  [%s].connected_clients = %s" % (i, s.connected_clients)
			print "  [%s].idling_connections = %s" % (i, cur_idle)
			print "  [%s].type = %s" % (i, s.type)
			print "  [%s].state = %s" % (i, s.state)

		if s.state != proxy.BACKEND_STATE_DOWN :
			#- try to connect to each backend once at least
			if cur_idle == 0 :
				proxy.connection.backend_ndx = i
				if is_debug :
					print "  ["+ str(i) +"] open new connection"
				return

			#- try to open at least min_idle_connections
			if least_idle_conns_ndx == -1 or\
				   ( cur_idle < min_idle_connections and\
					 cur_idle < least_idle_conns ) :
				least_idle_conns_ndx = i
				#least_idle_conns = s.idling_connections

	if least_idle_conns_ndx > -1 :
		proxy.connection.backend_ndx = least_idle_conns_ndx

	if proxy.connection.backend_ndx >= 0 :
		s = proxy.globals.backends[proxy.connection.backend_ndx]
		pool     = s.pool #- we don't have a username yet, try to find a connections which is idling
		try:
			cur_idle = pool.users[""].cur_idle_connections
		except:
			cur_idle = 0

		if cur_idle >= min_idle_connections :
			#- we have 4 idling connections in the pool, that's good enough
			if is_debug :
				print"  using pooled connection from: %s" % proxy.connection.backend_ndx

			return proxy.PROXY_IGNORE_RESULT

	if is_debug :
		print "  opening new connection on: %s" % proxy.connection.backend_ndx

	#- open a new connection

#--
#- put the successfully authed connection into the connection pool
#-
#- @param auth the context information for the auth
#-
#- auth.packet is the packet
def read_auth_result(proxy, auth ):
	if ord(auth.packet[0]) == proxy.MYSQLD_PACKET_OK :
		#- auth was fine, disconnect from the server
		proxy.connection.backend_ndx = -1
	#elif ord(auth.packet[0]) == proxy.MYSQLD_PACKET_EOF :
		#- we received either a
		#-
		#- * MYSQLD_PACKET_ERR and the auth failed or
		#- * MYSQLD_PACKET_EOF which means a OLD PASSWORD (4.0) was sent
	#	print "(read_auth_result) +. not ok yet"
	elif ord(auth.packet[0]) == proxy.MYSQLD_PACKET_ERR :
		#- auth failed
		pass


#--
#- read/write splitting
def read_query( proxy, packet ):
	if is_debug :
		print "[read_query]"
		print "  authed backend = %s" % proxy.connection.backend_ndx
		print "  used db = %s" % proxy.connection.client.default_db

	if ord(packet[0]) == proxy.COM_QUIT :
		#- don't send COM_QUIT to the backend. We manage the connection
		#- in all aspects.
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
		}

		return proxy.PROXY_SEND_RESULT

	if proxy.connection.backend_ndx == -1 :
		#- we don't have a backend right now
		#-
		#- let's pick a master as a good default
		for i, s in enumerate(proxy.globals.backends):
			pool     = s.pool #- we don't have a username yet, try to find a connections which is idling
			try:
				cur_idle = pool.users[proxy.connection.client.username].cur_idle_connections
			except:
				cur_idle = 0

			if cur_idle > 0 and\
					   s.state != proxy.BACKEND_STATE_DOWN and\
					   s.type == proxy.BACKEND_TYPE_RW :
				proxy.connection.backend_ndx = i
				break

	if True or proxy.connection.client.default_db and\
			proxy.connection.client.default_db != proxy.connection.server.default_db :
		#- sync the client-side default_db with the server-side default_db
		proxy.queries.append(2, chr(proxy.COM_INIT_DB) + proxy.connection.client.default_db,  True)
	proxy.queries.append(1, packet, True)

	return proxy.PROXY_SEND_QUERY

#--
#- as long as we are in a transaction keep the connection
#- otherwise release it so another client can use it
def read_query_result( proxy, inj ):
	res      = inj.resultset
  	flags    = res.flags

	if inj.id != 1 :
		#- ignore the result of the USE <default_db>
		return proxy.PROXY_IGNORE_RESULT

	proxy.globals.is_in_transaction = flags.in_trans

	if not proxy.globals.is_in_transaction :
		#- release the backend
		proxy.connection.backend_ndx = -1

#--
#- close the connections if we have enough connections in the pool
#-
#- @return nil - close connection
#-         IGNORE_RESULT - store connection in the pool
def disconnect_client(proxy):
	if is_debug :
		print "[disconnect_client]"

	if proxy.connection.backend_ndx == -1 :
		#- currently we don't have a server backend assigned
		#-
		#- pick a server which has too many idling connections and close one
		for i, s in enumerate(proxy.globals.backends):
			pool     = s.pool #- we don't have a username yet, try to find a connections which is idling
			try:
				cur_idle = pool.users[proxy.connection.client.username].cur_idle_connections
			except:
				cur_idle = 0

			if s.state != proxy.BACKEND_STATE_DOWN and\
					   cur_idle > max_idle_connections :
				#- try to disconnect a backend
				proxy.connection.backend_ndx = i
				if is_debug :
					print "  [%s] closing connection, idling: %s" % (i, cur_idle)
				return
