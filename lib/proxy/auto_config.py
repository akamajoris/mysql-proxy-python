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


import re
#--
#- automatic configure of modules
#- SHOW CONFIG

#--
#- transform a table into loadable string
def tbl2str(tbl, indent=""):
	s = ""
	for k, v in tbl.items():
		s += indent + ("[%s] : " % k)
		if type(v) == "table" :
			s += "{\n" + tbl2str(v, indent + "  ") + indent + "}"
		elif type(v) == "string" :
			s += "%s" % v
		else:
			s += repr(v)
		s += ",\n"

	return s


#--
#- turn a string into a case-insensitive lpeg-pattern
#-

#'PROXY SHOW CONFIG'
#'PROXY SET GLOBAL a.b=value'
#'PROXY SAVE CONFIG INTO "conf"'
#'PROXY LOAD CONFIG FROM "conf"'
lang =\
re.compile('\s*proxy\s+(((show)\s+config)|((set)\s+global\s+(\w+)\.(\w+)\s*=\s*(?P<bool_true>(true)|(?P<bool_false>false)|(?P<string>\"\w+\")|(?P<number>\d+)))|((save)\s+config\s+into\s+(\".*\"))|((load)\s+config\s+from\s+(\".*\")))\s*', re.I)

SET_VALUE_PARSE = {
	'bool_true' : lambda x:True,
	'bool_false' : lambda x:False,
	'string' : str,
	'number' : long,
}

def get_tokens(m, string):
	try:
		groups = m.match(string).groups()
	except AttributeError:
		return None

	groupdict = m.match(string).groupdict()
	start = seq_find(groups[1:], groups[0])
	start += 2
	if groups[start].lower() == 'set':
		for k, v in groupdict.items():
			if v is not None:
				return list(groups[start:start+3]) + [SET_VALUE_PARSE[k](v)]
	return groups[start:]

def seq_find(seq, item):
	for i,it in enumerate(seq):
		if it == item:
			return i

def handle(tbl, proxy, cmd=None):
	#--
	#- support old, deprecated API:
	#-   auto_config.handle(cmd)
	#- and map it to
	#-   proxy.globals.config:handle(cmd)
	if cmd == None and type(tbl.type) in (int, long, float):
		cmd = tbl
		tbl = proxy.globals.config

	#- handle script-options first
	if cmd.type != proxy.COM_QUERY :
		return None

	#- don't try to tokenize log SQL queries
	if len(cmd.query) > 128 :
		return None

	tokens = get_tokens(lang, cmd.query)

	if not tokens :
		return None

	if tokens[0].upper() == "SET" :
		if not tbl.has_key(tokens[1]) :
			proxy.response = {
				'type' : proxy.MYSQLD_PACKET_ERR,
				'errmsg' : "module not known",
			}
		elif not tbl[tokens[1]].has_key(tokens[2]) :
			proxy.response = {
				'type' : proxy.MYSQLD_PACKET_ERR,
				'errmsg' : "option not known"
			}
		else:
			tbl[tokens[1]][tokens[2]] = tokens[3]
			proxy.response = {
				'type' : proxy.MYSQLD_PACKET_OK,
				'affected_rows' : 1
			}

	elif tokens[0] == "SHOW" :
		rows = []

		for mod, options in tbl.items():
			for option, val in options.items():
				rows.append((mod, options, str(val), type(val)))

		proxy.response = {
			'type' : proxy.MYSQLD_PACKET_OK,
			'resultset' : {
				'fields' : (
					( "module", proxy.MYSQL_TYPE_STRING ),
					( "option", proxy.MYSQL_TYPE_STRING ),
					( "value", proxy.MYSQL_TYPE_STRING ),
					( "type", proxy.MYSQL_TYPE_STRING ),
				),
				'rows' : rows,
			}
		}
	elif tokens[0] == "SAVE" :
		#- save the config into this filename
		filename = tokens[1]
		ret, errmsg = save(tbl, filename)
		if ret:
			proxy.response = {
				'type' : proxy.MYSQLD_PACKET_OK,
				'affected_rows' : 0,
			}
		else:
			proxy.response = {
				'type' : proxy.MYSQLD_PACKET_ERR,
				'errmsg' : errmsg
			}

	elif tokens[0] == "LOAD" :
		filename = tokens[2]

		ret, errmsg =  load(tbl, filename)

		if ret :
			proxy.response = {
				'type' : proxy.MYSQLD_PACKET_OK,
				'affected_rows' : 0
			}
		else:
			proxy.response = {
				'type' : proxy.MYSQLD_PACKET_ERR,
				'errmsg' : errmsg
			}
	else:
		assert(False)

	return proxy.PROXY_SEND_RESULT


def save(tbl, filename):
	content = "{" + tbl2str(tbl, "  ") + "}"

	f = open(filename, "w")

	if not f:
		return False, errmsg

	f.write(content)
	f.close()

	return [True]


def load(tbl, filename):
	func = open(filename).read()

	if not func :
		return False, errmsg

	v = eval(func)

	for mod, options in v.items():
		if tbl[mod]:
			#- weave the loaded options in
			for option, value in options.items():
				tbl[mod][option] = value
		else:
			tbl[mod] = options

	return [True]
