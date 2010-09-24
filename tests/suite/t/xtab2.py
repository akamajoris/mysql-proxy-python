
import os, sys
sys.path.append(os.environ['PYTHON_LIBPATH'])

import xtab

#connect_server = admin_sql.connect_server
#read_auth_result = admin_sql.read_auth_result
read_query = xtab.read_query
read_query_result = xtab.read_query_result
#disconnect_client = admin_sql.disconnect_client
