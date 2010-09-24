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



import os, sys
sys.path.append(os.environ['PYTHON_LIBPATH'])

DEBUG = os.getenv('DEBUG') or os.getenv('VERBOSE')  or 0
DEBUG = int(DEBUG)

xtab_version = '0.1.3'

import proxy.tokenizer as tokenizer

xtab_error_status = 0
return_xtab_query = False

xtab_help_messages = (
    ('xtab - version ' + xtab_version + ' - (C) MySQL AB 2007' ,) ,
    ('Syntax: ' ,) ,
    (' - ' ,) ,
    ('XTAB table_name row_header col_header operation operation_fld [summary]',),
    ('"table_name" can be a table or a view' ,) ,
    ('"row_field" is the field to be used as row header' ,) ,
    ('"col_field" is the field whose distinct values will become column headers',),
    ('"operation" is the required operation (COUNT|SUM|AVG|MAX|MIN)' ,) ,
    ('"operation_field" is the field to which the operation is applied' ,) ,
    (' - ' ,) ,
    ('If the "summary" option is used, then a "WITH ROLLUP" clause ' ,),
    ('is added to the query.' ,) ,
    (' - ' ,) ,
    ('Other commands:' ,) ,
    ('XTAB QUERY - the XTAB query is returned instead of its result' ,) ,
    ('XTAB NOQUERY - the XTAB result is returned (default)' ,) ,
    ('XTAB version - shows current version' ,) ,
    ('XTAB help - shows this help' ,) ,
    ('Created by Giuseppe Maxia' ,) ,
)

allowed_operators = ('count', 'sum', 'avg', 'min', 'max' )

#-
#- Result with the syntax help
#-
xtab_help_resultset = {
    'fields' : (
        ('XTAB help', proxy.MYSQL_TYPE_STRING),
    ),
    'rows' : xtab_help_messages,
}

#-
#- Result with the XTAB version
#-
xtab_version_resultset = {
    'fields' : (
        ('XTAB version', proxy.MYSQL_TYPE_STRING),
    ),
    'rows' : (
        (xtab_version,) ,
    )
}

#-
#- Result to comment on XTAB QUERY command
#-
xtab_query_resultset = {
    'fields' : (
        ( 'XTAB query ', proxy.MYSQL_TYPE_STRING),
    ),
    'rows' : (
        ('Setting XTAB QUERY, the next XTAB command will return ' ,),
        ('the query text instead of its result.' ,),
        ('' ,),
        ('Setting XTAB NOQUERY (default), the XTAB command' ,),
        ('executes the query and returns its result.' ,),
        ('' ,),
    )
}

#-
#- result returned on wrong XTAB option
#-
xtab_unknown_resultset = {
    'fields' : (
        ( 'XTAB ERROR', proxy.MYSQL_TYPE_STRING),
    ),
    'rows' : (
        ('unknown command. Enter "XTAB HELP" for help',),
    )
}

#-
#- result returned on wrong operator
#-
xtab_unknown_operator = {
    'fields' : (
        ( 'XTAB ERROR', proxy.MYSQL_TYPE_STRING),
    ),
    'rows' : (
        ('unknown operator.',),
        ( 'Accepted operators: COUNT, SUM, AVG, MIN, MAX', ),
        ( 'Enter "XTAB HELP" for help', ),
    )
}

#-
#- xtab parameters to be passed from read_query ro read_query_result 
#-
xtab_params = {}

xtab_id_before = 1024
xtab_id_start  = 2048
xtab_id_exec   = 4096


def read_query( proxy, packet ):
	if ord(packet[0]) != proxy.COM_QUERY :
		return

	xtab_params = {}
	xtab_error_status = 0

	query = packet[1:]
	#-
	#- simple tokeninzing the query, looking for accepted pattern
	#-
	#local option, table_name, row_field, col_field , op, op_col , summary
	query_tokens = tokenizer.tokenize(query)
	START_TOKEN = 0

	if  ( query_tokens[0].text.lower() == 'xtab' ):
		START_TOKEN = 1
		option = query_tokens[1].text
	elif ( query_tokens[0].text.lower() == 'select'\
		  and\
		  query_tokens[1].text.lower() == 'xtab' ):
		START_TOKEN = 2
		option = query_tokens[2].text
	else:
		return

	print_debug('received query ' + query)
	if len(query_tokens) == START_TOKEN + 1:
		if (option.lower() == 'help'):
			proxy.response.resultset = xtab_help_resultset
			f, r = proxy.response.resultset.fields, proxy.response.resultset.rows
		elif option.lower() == 'version' :
			proxy.response.resultset = xtab_version_resultset
		elif option.lower() == 'query' :
			#xtab_query_resultset['rows'].append(( 'Current setting: returns a query', ))
			#proxy.response.resultset = xtab_query_resultset
			proxy.response.resultset = {
				'fields' : xtab_query_resultset['fields'],
				'rows' : xtab_query_resultset['rows'] + (('Current setting: returns a query', ), ),
			}
			return_xtab_query = True
		elif option.lower() == 'noquery' :
			#xtab_query_resultset['rows'].append(( 'Current setting: returns a result set', ))
			#proxy.response.resultset = xtab_query_resultset
			proxy.response.resultset = {
				'fields' : xtab_query_resultset['fields'],
				'rows' : xtab_query_resultset['rows'] + (('Current setting: returns a result set', ), ),
			}
			return_xtab_query = False
		else:
			proxy.response.resultset = xtab_unknown_resultset
		proxy.response.type = proxy.MYSQLD_PACKET_OK
		return proxy.PROXY_SEND_RESULT

	#-
	#- parsing the query for a xtab recognized command
	#-
	table_name = option
	row_field  = query_tokens[START_TOKEN + 1 ].text
	col_field  = query_tokens[START_TOKEN + 2 ].text
	op         = query_tokens[START_TOKEN + 3 ].text
	op_col     = query_tokens[START_TOKEN + 4 ].text
	if (query_tokens[START_TOKEN + 5 ] ) :
		summary    = query_tokens[START_TOKEN + 5 ].text
	else:
		summary = ''
	if op_col :
		print_debug ("<xtab> <%s> (%s) (%s) [%s] [%s]" % \
			(table_name, row_field, col_field, op, op_col ))
	else:
		return

	recognized_operator = op.lower() in allowed_operators

	if not recognized_operator:
		print_debug('unknown operator ' + op)
		proxy.response.type = proxy.MYSQLD_PACKET_OK
		proxy.response.resultset = xtab_unknown_operator
		return proxy.PROXY_SEND_RESULT

	xtab_params['table_name'] = table_name
	xtab_params['row_header'] = row_field
	xtab_params['col_header'] = col_field
	xtab_params['operation']  = op
	xtab_params['op_col']     = op_col
	xtab_params['summary']    = summary.lower() == 'summary'

	print_debug('summary: ' + xtab_params['summary'])

	proxy.queries.append(xtab_id_before,
		chr(proxy.COM_QUERY) + "set group_concat_max_len = 1024*1024", true)

	proxy.queries.append(xtab_id_start,
		chr(proxy.COM_QUERY) +
		string.format('''
		  select group_concat( distinct concat(
			'%s(if( `%s`= ', quote(%s),',`%s`,null)) as `%s_',%s,'`' )
			 order by `%s` ) from `%s` order by `%s`''' %\
			(op,
			col_field,
			col_field,
			op_col,
			col_field,
			col_field,
			col_field,
			table_name,
			col_field, )
		), true)
	return proxy.PROXY_SEND_QUERY

def read_query_result(proxy, inj):
	print_debug('injection id ' +  inj.id + ' error status: ' + xtab_error_status)
	if xtab_error_status > 0 :
		print_debug('ignoring resultset ' + inj.id + ' for previous error')
		return proxy.PROXY_IGNORE_RESULT
	res = inj.resultset
	#-
	#- on error, empty the query queue and return the error message
	#-
	if res.query_status and res.query_status < 0:
		xtab_error_status = 1
		print_debug('sending result' + inj.id + ' on error ')
		proxy.queries.reset()
		return

	#-
	#- ignoring the preparatory queries
	#-
	if (inj.id >= xtab_id_before) and (inj.id < xtab_id_start) :
		print_debug ('ignoring preparatory query from xtab ' + inj.id )
		return proxy.PROXY_IGNORE_RESULT

	#-
	#- creating the XTAB query
	#-
	if (inj.id == xtab_id_start) :
		print_debug ('getting columns resultset from xtab ' + inj.id )
		col_query = ''

		for row in inj.resultset.rows:
			col_query = col_query + row[0]

		print_debug ('column values : ' + col_query)
		#TODO
		col_query.replace(',' + xtab_params['operation'], '\n, ' + xtab_params['operation'])
		xtab_query = '''
		  SELECT
			%s ,
			%s ,
			%s(`%s`) AS total
		  FROM %s
		  GROUP BY %s
		''' % \
			(xtab_params['row_header'],
			col_query,
			xtab_params['operation'],
			xtab_params['op_col'],
			xtab_params['table_name'],
			xtab_params['row_header'])
		if xtab_params['summary'] == True :
			xtab_query = xtab_query + ' WITH ROLLUP '
		#-
		#- if the query was requested, it is returned immediately
		#-
		if (return_xtab_query == True) :
			proxy.queries.reset()
			proxy.response.type = proxy.MYSQLD_PACKET_OK
			proxy.response.resultset = {
				'fields' : (
					('XTAB query', proxy.MYSQL_TYPE_STRING),
				),
				rows : [
					[ xtab_query, ],
				]
			}
			return proxy.PROXY_SEND_RESULT
		#-
		#- The XTAB query is executed
		#-
		proxy.queries.append(xtab_id_exec, chr(proxy.COM_QUERY) + xtab_query, True)
		print_debug (xtab_query, 2)
		return proxy.PROXY_IGNORE_RESULT

	#-
	#- Getting the final xtab result
	#-
	if (inj.id == xtab_id_exec) :
		print_debug ('getting final xtab result ' + inj.id )
		#-
		#- Replacing the default NULL value provided by WITH ROLLUP
		#- with a more human readable value
		#-
		if xtab_params['summary'] == True :
			updated_rows = {}
			updated_fields = {}
			for row in inj.resultset.rows:
				if not row:
					row[0] = 'Grand Total'
				end
				updated_rows.append(row)
			field_count = 1
			fields = inj.resultset.fields

			for f in fields:
				updated_fields.append((f.name, f.type))
			proxy.response.resultset = {
				'fields' : updated_fields,
				'rows' : updated_rows
			}
			proxy.response.type = proxy.MYSQLD_PACKET_OK
			return proxy.PROXY_SEND_RESULT

def print_debug (msg, min_level=0):
    #if DEBUG and (DEBUG >= min_level) :
	print msg
