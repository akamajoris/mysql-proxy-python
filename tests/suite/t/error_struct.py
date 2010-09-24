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


def packet_auth(fields = {}):
	return "\x0a" +\
		fields.get('version', "5.0.45-proxy") +\
		"\000" +\
		"\001\000\000\000" +\
		"\x41\x41\x41\x41" +\
		"\x41\x41\x41\x41" +\
		"\000" +\
		"\001\x82" +\
		"\x08" +\
		"\002\000" +\
		"\000" * 13 +\
		"\x41\x41\x41\x41" +\
		"\x41\x41\x41\x41" +\
		"\x41\x41\x41\x41" +\
		"\000"                #- challenge - part II

def connect_server(proxy):
	#- emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (
			packet_auth(),
		)
	}
	return proxy.PROXY_SEND_RESULT


def read_query(proxy, packet ):
	if ord(packet[0]) != proxy.COM_QUERY:
		proxy.response = { 'type' : proxy.MYSQLD_PACKET_OK }
		return proxy.PROXY_SEND_RESULT

	import re
	m = re.search('^\s*select\s+error\s+(\d+)\s+(\w+)\s+"(.*)"', packet[1:].lower())
	if m:
		err_code, sql_state, err_msg = m.groups()
	else:
		err_code, sql_state, err_msg = None, None, None
	print '<%s>, <%s>, <%s>' % (err_code, sql_state, err_msg)

	if err_code and sql_state:
		try:
			proxy.response = {
				'type'     : proxy.MYSQLD_PACKET_ERR,
				'errmsg'   : err_msg,
				'errcode'  : int(err_code),
				'sqlstate' : sql_state
			}
			return proxy.PROXY_SEND_RESULT
		except:
			pass
