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

import admin_sql


def connect_server(proxy):
	print 'admin-sql connect server'

#connect_server = admin_sql.connect_server
#read_auth_result = admin_sql.read_auth_result
read_query = admin_sql.read_query
read_query_result = admin_sql.read_query_result
#disconnect_client = admin_sql.disconnect_client
