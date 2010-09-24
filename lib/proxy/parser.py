
def tablename_expand(tblname, db_name):
	if not db_name:
		db_name = proxy.connection.client.default_db
	if db_name:
		tblname = db_name + "." + tblname

	return tblname


#--
#- extract the table-names from tokenized SQL token stream
#-
#- @see proxy.tokenize
def get_tables(tokens):
	sql_stmt = None
	in_tablelist = False
	next_is_tblname = False
	in_braces = 0
	db_name = None

	tables = {}

	for i, token in enumerate(tokens):

		#- print(i + " token: " + token["token_name"])
		if token.token_name in ("TK_COMMENT", "TK_UNKNOWN"):

		elif not sql_stmt:
			#- try to get the SQL stmt
			sql_stmt = token.text.upper()
			#- print(i + " sql-stmt: " + sql_stmt)

			if sql_stmt in ("UPDATE", "INSERT"):
				in_tablelist = True

		elif sql_stmt in ("SELECT", "DELETE"):
			#- we have sql_stmt token already, try to get the table names
			#-
			#- SELECT +. FROM tbl AS alias, +.
			#- DELETE FROM +.

			if in_tablelist:
				if token.token_name == "TK_COMMA":
					next_is_tblname = True
				elif in_braces > 0:
					#- ignore sub-queries
				elif token.token_name == "TK_SQL_AS":
					#- FROM tbl AS alias +.
					next_is_tblname = False
				elif token.token_name == "TK_SQL_JOIN":
					#- FROM tbl JOIN tbl +.
					next_is_tblname = True
				elif token.token_name in ("TK_SQL_LEFT", "TK_SQL_RIGHT",
						"TK_SQL_OUTER", "TK_SQL_USING", "TK_SQL_ON",
						"TK_SQL_AND", "TK_SQL_OR"):
					#- ignore me
					pass
				elif token.token_name == "TK_LITERAL" and next_is_tblname:
					#- we have to handle <tbl> and <db>.<tbl>
					if not db_name and len(tokens) > i + 1 and tokens[i + 1].token_name == "TK_DOT":
						db_name = token.text
					else:
						tables[tablename_expand(token.text, db_name)] = (sql_stmt == "SELECT" and "read" or "write")

						db_name = None

					next_is_tblname = False
				elif token["token_name"] == "TK_OBRACE":
					in_braces = in_braces + 1
				elif token["token_name"] == "TK_CBRACE":
					in_braces = in_braces - 1
				elif token["token_name"] in ("TK_SQL_WHERE", "TK_SQL_GROUP",
						"TK_SQL_ORDER", "TK_SQL_LIMIT", "TK_CBRACE"):
					in_tablelist = False
				elif token["token_name"] == "TK_DOT":
					#- FROM db.tbl
					next_is_tblname = True
				else:
					print "(parser) unknown, found token: " + token.token_name + " -> " + token.text
					#- in_tablelist = False
				
			elif token.token_name == "TK_SQL_FROM":
				in_tablelist = True
				next_is_tblname = True
			
			
			#- print(i + " in-from: " + (in_from and "True" or "False"))
			#- print(i + " next-is-tblname: " + (next_is_tblname and "True" or "False"))
		elif sql_stmt in ("CREATE", "DROP", "ALTER", "RENAME"):
			#- CREATE TABLE <tblname>
			if not ddl_type:
				ddl_type = token.text.upper()
				in_tablelist = True
			elif ddl_type == "TABLE":
				if in_tablelist and token.token_name == "TK_LITERAL":
					tables[tablename_expand(token.text)] = (sql_stmt == "SELECT" and "read" or "write")
				else:
					in_tablelist = False
					break

		elif sql_stmt == "INSERT":
			#- INSERT INTO +.
			if in_tablelist:
				if token["token_name"] == "TK_LITERAL":
					tables[tablename_expand(token.text)] = (sql_stmt == "SELECT" and "read" or "write")
				elif token["token_name"] == "TK_SQL_INTO":
					pass
				else:
					in_tablelist = False

		elif sql_stmt == "UPDATE":
			#- UPDATE <tbl> SET +
			if in_tablelist:
				if token["token_name"] == "TK_LITERAL":
					tables[tablename_expand(token.text)] = (sql_stmt == "SELECT" and "read" or "write")
				elif token["token_name"] == "TK_SQL_SET":
					in_tablelist = False

					break

	return tables



