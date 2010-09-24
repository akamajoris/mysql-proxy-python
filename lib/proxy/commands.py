
#--
#- map the constants to strings
#- lua starts at 1
command_names = (
	"COM_SLEEP",
	"COM_QUIT",
	"COM_INIT_DB",
	"COM_QUERY",
	"COM_FIELD_LIST",
	"COM_CREATE_DB",
	"COM_DROP_DB",
	"COM_REFRESH",
	"COM_SHUTDOWN",
	"COM_STATISTICS",
	"COM_PROCESS_INFO",
	"COM_CONNECT",
	"COM_PROCESS_KILL",
	"COM_DEBUG",
	"COM_PING",
	"COM_TIME",
	"COM_DELAYED_INSERT",
	"COM_CHANGE_USER",
	"COM_BINLOG_DUMP",
	"COM_TABLE_DUMP",
	"COM_CONNECT_OUT",
	"COM_REGISTER_SLAVE",
	"COM_STMT_PREPARE",
	"COM_STMT_EXECUTE",
	"COM_STMT_S_LONG_DATA",
	"COM_STMT_CLOSE",
	"COM_STMT_RESET",
	"COM_SET_OPTION",
	"COM_STMT_FETCH",
	"COM_DAEMON"
)

#--
#- split a MySQL command packet into its parts
#-
#- @param packet a network packet
#- @return a table with .type, .type_name and command specific fields 

class generic(object):
	def __init__(self, value=None):
		if type(value) == dict:
			for k, v in value.items():
				setattr(self, k, v)

def parse(packet):
	cmd = generic()

	cmd.type = ord(packet[0])
	cmd.type_name = command_names[cmd.type + 1]
	if cmd.type == proxy.COM_QUERY:
		cmd.query = packet[1:]
	elif cmd.type in (proxy.COM_QUIT, proxy.COM_PING, proxy.COM_SHUTDOWN):
		#- nothing to decode
		pass
	elif cmd.type == proxy.COM_STMT_PREPARE:
		cmd.query = packet[1:]
	#- the stmt_handler_id is at the same position for both STMT_EXECUTE and STMT_CLOSE
	elif cmd.type in (proxy.COM_STMT_EXECUTE, proxy.COM_STMT_CLOSE):
		cmd.stmt_handler_id = ord(packet[1]) + ord(packet[2]) * 256 +\
				ord(packet[3]) * 256 * 256 + ord(packet[4]) * 256 * 256 * 256
	elif cmd.type == proxy.COM_FIELD_LIST:
		cmd.table = packet[1:]
	elif cmd.type in (proxy.COM_INIT_DB, proxy.COM_CREATE_DB, proxy.COM_DROP_DB):
		cmd.schema = packet[1:]
	elif cmd.type == proxy.COM_SET_OPTION:
		cmd.option = packet[1:]
	else:
		print("[debug] (command) unhandled type name:" + str(cmd.type_name) + " byte:" + str(cmd.type))

	return cmd


def pretty_print(cmd):
	if cmd.type in (proxy.COM_QUERY, proxy.COM_STMT_PREPARE):
		return "[%s] %s" % (cmd.type_name, cmd.query)
	elif cmd.type == proxy.COM_INIT_DB:
		return "[%s] %s" % (cmd.type_name, cmd.schema)
	elif cmd.type in (proxy.COM_QUIT, proxy.COM_PING, proxy.COM_SHUTDOWN):
		return "[%s]" % cmd.type_name
	elif cmd.type == proxy.COM_FIELD_LIST:
		#- should have a table-name
		return "[%s]" % cmd.type_name
	elif cmd.type == proxy.COM_STMT_EXECUTE:
		return "[%s] %s" % (cmd.type_name, cmd.stmt_handler_id)
	elif cmd.type == proxy.COM_STMT_EXECUTE:
		return "[%s] %s" % (cmd.type_name, cmd.stmt_handler_id)

	return "[%s] ... no idea" % cmd.type_name
