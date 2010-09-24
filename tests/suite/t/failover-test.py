
import os, sys
sys.path.append(os.environ['PYTHON_LIBPATH'])

import admin_sql

#connect_server = admin_sql.connect_server
#read_auth_result = admin_sql.read_auth_result
read_query = admin_sql.read_query
read_query_result = admin_sql.read_query_result
#disconnect_client = admin_sql.disconnect_client
