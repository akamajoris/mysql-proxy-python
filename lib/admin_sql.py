##-
#- map SQL commands to the hidden MySQL Protocol commands
#-
#- some protocol commands are only available through the mysqladmin tool like
#- * ping
#- * shutdown
#- * debug
#- * statistics
#-
#- +. while others are avaible
#- * process info (SHOW PROCESS LIST)
#- * process kill (KILL <id>)
#-
#- +. and others are ignored
#- * time
#-
#- that way we can test MySQL Servers more easily with "mysqltest"
#-


##-
#- recognize special SQL commands and turn them into COM_* sequences
#-
def read_query(proxy, packet):
	if ord(packet[0]) != proxy.COM_QUERY :
		return

	if packet[1:] == "COMMIT SUICIDE" :
		proxy.queries.append(proxy.COM_SHUTDOWN, chr(proxy.COM_SHUTDOWN), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "PING" :
		proxy.queries.append(proxy.COM_PING, chr(proxy.COM_PING), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "STATISTICS" :
		proxy.queries.append(proxy.COM_STATISTICS, chr(proxy.COM_STATISTICS), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "PROCINFO" :
		proxy.queries.append(proxy.COM_PROCESS_INFO, chr(proxy.COM_PROCESS_INFO), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "TIME" :
		proxy.queries.append(proxy.COM_TIME, chr(proxy.COM_TIME), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "DEBUG" :
		proxy.queries.append(proxy.COM_DEBUG, chr(proxy.COM_DEBUG), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "PROCKILL" :
		proxy.queries.append(proxy.COM_PROCESS_KILL, chr(proxy.COM_PROCESS_KILL), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "SETOPT" :
		proxy.queries.append(proxy.COM_SET_OPTION, chr(proxy.COM_SET_OPTION), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "BINLOGDUMP" :
		proxy.queries.append(proxy.COM_BINLOG_DUMP, chr(proxy.COM_BINLOG_DUMP), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "BINLOGDUMP1" :
		proxy.queries.append(proxy.COM_BINLOG_DUMP,
			chr(proxy.COM_BINLOG_DUMP) +\
			"\x04\x00\x00\x00" +\
			"\x00\x00" +\
			"\x02\x00\x00\x00" +\
			"\x00" +\
			""
			, True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "REGSLAVE" :
		proxy.queries.append(proxy.COM_REGISTER_SLAVE, chr(proxy.COM_REGISTER_SLAVE), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "REGSLAVE1" :
		proxy.queries.append(proxy.COM_REGISTER_SLAVE,
			chr(proxy.COM_REGISTER_SLAVE) +\
			"\x01\x00\x00\x00" +\
			"\x00" +\
			"\x00" +\
			"\x00" +\
			"\x01\x00" +\
			"\x00\x00\x00\x00" +\
			"\x01\x00\x00\x00" +\
			""
			, True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "PREP" :
		proxy.queries.append(proxy.COM_STMT_PREPARE, chr(proxy.COM_STMT_PREPARE), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "PREP1" :
		proxy.queries.append(proxy.COM_STMT_PREPARE, chr(proxy.COM_STMT_PREPARE) + "SELECT ?", True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "EXEC" :
		proxy.queries.append(proxy.COM_STMT_EXECUTE, chr(proxy.COM_STMT_EXECUTE), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "EXEC1" :
		proxy.queries.append(proxy.COM_STMT_EXECUTE,
			chr(proxy.COM_STMT_EXECUTE) +\
			"\x01\x00\x00\x00" +\
			"\x00" +\
			"\x01\x00\x00\x00" +\
			"\x00"             +\
			"\x01"             +\
			"\x00\xfe" +\
			"\x04" + "1234" +\
			"", True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "DEAL" :
		proxy.queries.append(proxy.COM_STMT_CLOSE, chr(proxy.COM_STMT_CLOSE), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "DEAL1" :
		proxy.queries.append(proxy.COM_STMT_CLOSE, chr(proxy.COM_STMT_CLOSE) + "\x01\x00\x00\x00", True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "RESET" :
		proxy.queries.append(proxy.COM_STMT_RESET, chr(proxy.COM_STMT_RESET), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "RESET1" :
		proxy.queries.append(proxy.COM_STMT_RESET, chr(proxy.COM_STMT_RESET) + "\x01\x00\x00\x00", True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "FETCH" :
		proxy.queries.append(proxy.COM_STMT_FETCH, chr(proxy.COM_STMT_FETCH), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "FETCH1" :
		proxy.queries.append(proxy.COM_STMT_FETCH, chr(proxy.COM_STMT_FETCH) +
				"\x01\x00\x00\x00" + "\x80\x00\x00\x00", True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "FLIST" :
		proxy.queries.append(proxy.COM_FIELD_LIST, chr(proxy.COM_FIELD_LIST), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "FLIST1" :
		proxy.queries.append(proxy.COM_FIELD_LIST, chr(proxy.COM_FIELD_LIST) + "t1\x00id\x00\x00\x00", True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "TDUMP" :
		proxy.queries.append(proxy.COM_TABLE_DUMP, chr(proxy.COM_TABLE_DUMP), True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "TDUMP1" :
		proxy.queries.append(proxy.COM_TABLE_DUMP, chr(proxy.COM_TABLE_DUMP) + "\x04test\x02t1", True)
		return proxy.PROXY_SEND_QUERY
	elif packet[1:] == "TDUMP2" :
		proxy.queries.append(proxy.COM_TABLE_DUMP, chr(proxy.COM_TABLE_DUMP) + "\x04test\x02t2", True)
		return proxy.PROXY_SEND_QUERY


##-
#- adjust the response to match the needs of COM_QUERY
#- where neccesary
#-
#- * some commands return EOF (COM_SHUTDOWN),
#- * some are plain-text (COM_STATISTICS)
#-
#- in the  the client sent us a COM_QUERY and we have to hide
#- all those specifics
def read_query_result(proxy, inj):

	if inj.id == proxy.COM_SHUTDOWN or\
			   inj.id == proxy.COM_SET_OPTION or\
			   inj.id == proxy.COM_BINLOG_DUMP or\
			   inj.id == proxy.COM_STMT_PREPARE or\
			   inj.id == proxy.COM_STMT_FETCH or\
			   inj.id == proxy.COM_FIELD_LIST or\
			   inj.id == proxy.COM_TABLE_DUMP or\
			   inj.id == proxy.COM_DEBUG :
		#- translate the EOF packet from the COM_SHUTDOWN into a OK packet
		#- to match the needs of the COM_QUERY we got
		if ord(inj.resultset.raw[0]) != 255 :
			proxy.response = {
				'type' : proxy.MYSQLD_PACKET_OK,
			}
			return proxy.PROXY_SEND_RESULT

	elif inj.id == proxy.COM_PING or\
			   inj.id == proxy.COM_TIME or\
			   inj.id == proxy.COM_PROCESS_KILL or\
			   inj.id == proxy.COM_REGISTER_SLAVE or\
			   inj.id == proxy.COM_STMT_EXECUTE or\
			   inj.id == proxy.COM_STMT_RESET or\
			   inj.id == proxy.COM_PROCESS_INFO :
		pass
		#- no change needed
	elif inj.id == proxy.COM_STATISTICS :
		#- the response a human readable plain-text
		#-
		#- just turn it into a proper result-set
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : [
					[ "statisitics", proxy.MYSQL_TYPE_STRING ]
				],
				'rows' : [
					[ inj.resultset.raw ]
				]
			}
		}
		return proxy.PROXY_SEND_RESULT

	else:
		#- we don't know them yet, just return ERR to the client to
		#- match the needs of COM_QUERY
		print "got: %s" % (inj.resultset.raw)
		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_ERR,
		}
		return proxy.PROXY_SEND_RESULT


