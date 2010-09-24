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

#-[[


#-]]


from proxy_utils import get_query_type, get_query_content
def str2hex(s):
  raw_len = len(s)
  i = 0
  o = ""
  while i < raw_len:
    o = o + " %02x" % ord(s[i])
    i += 1

  return o

#-
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
	"COM_STMT_SEND_LONG_DATA",
	"COM_STMT_CLOSE",
	"COM_STMT_RESET",
	"COM_SET_OPTION",
	"COM_STMT_FETCH",
	"COM_DAEMON"
)

#-- dump the result-set to stdout
#-
#- @param inj "packet.injection"
def dump_query_result( inj ):
  try:
      fields = inj.resultset.fields
  except:
      fields = []

  print 'The resultset is:'
  for i, field in enumerate(fields):
    print "| | field[%s] = {%s, %s}" % (i, field.type, field.name)

  try:
      rows = inj.resultset.rows
  except:
      rows = []
  for i, row in enumerate(rows):
    o = None
    for j in xrange(len(inj.resultset.fields)):
      if o is None:
        o = ""
      else:
        o += ", "
      if not row[j] :
        o += "(None)"
      else:
        o += row[j]
    print "| | row[%s] = { %s }" % (i, row)

def decode_query_packet( packet ):
  #- we don't have the packet header in the
  packet_len = len(packet)
  it = iter(map(ord, packet))

  print "| query.len = %s" % packet_len
  print "| query.packet =" + str2hex(packet)
  #- print("(decode_query) " + "| packet-id = " + "(unknown)")

  print "| .#-- query"
  pt = it.next()
  print "| | command = " + command_names[pt]
  if pt == proxy.COM_QUERY :
    #- after the COM_QUERY comes the query
	print "| | query = " + packet[1:]

  elif pt == proxy.COM_INIT_DB :
    print "| | db = " + packet[1:]

  elif pt == proxy.COM_STMT_PREPARE :
    print("| | query = " + packet[1:])

  elif pt == proxy.COM_STMT_EXECUTE :
    stmt_handler_id = it.next() + (it.next() * 256) +\
			(it.next() * 256 * 256) + (it.next() * 256 * 256 * 256)
    flags = it.next()
    iteration_count = it.next() + (it.next() * 256) + (it.next() * 256 * 256) +\
			(it.next() * 256 * 256 * 256)

    print "| | stmt-id = %s" % stmt_handler_id
    print "| | flags = %s" % string.format("%02x", flags)
    print "| | iteration_count = %s" % iteration_count

    if packet_len > 10 :
      #- if we don't have any place-holders, no for NUL and friends
      nul_bitmap = it.next()
      new_param  = it.next()

      print "| | nul_bitmap = " + "%02x" % nul_bitmap
      print "| | new_param = %s" % new_param
    else:
      print "| | (no params)"

    print "| | prepared-query = %s" % prepared_queries[stmt_handler_id]
  else:
    print "| | packet =" + str2hex(packet)
  print "| '#--"


def read_query(proxy, packet):

#-[[	for i = 1, #proxy.global.backends do
        #print("  ["+ i +"].connected_clients = " + s.connected_clients)
        #print("  ["+ i +"].idling_connections = " + cur_idle)
        #print("  ["+ i +"].type = " + s.type)
        #print("  ["+ i +"].state = " + s.state)
    #end
#-]]

	if get_query_type(packet) == proxy.COM_QUERY:
		proxy.queries.append(1, chr(proxy.COM_QUERY) + "SELECT NOW()", True)
		if proxy.connection :
			try:
				print  "inject monitor query into backend # %s" % proxy.connection.backend_ndx
			except:
				print '-' * 50, 'An error:'
				import traceback
				print traceback.format_exc()
		else:
			print "inject monitor query"
		return proxy.PROXY_SEND_QUERY

def read_query_result ( proxy, inj ):

	res      = inj.resultset
	packet   = inj.query

	decode_query_packet(packet)

	if inj.id == 1:
		dump_query_result(inj)
