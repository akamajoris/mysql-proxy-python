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

#--
#- Bug #35729
#-
#- a value from the 1st column randomly becomes nil even if we send back
#- a value from the mock server
#-
#- it only happens for the 2nd resultset we receive

#--
#- duplicate the test-query
def read_query( proxy, packet ):
	if ord(packet[0]) == proxy.COM_QUERY :
		proxy.queries.append(1, packet, True )
		return proxy.PROXY_SEND_QUERY

#--
#- check that the 2nd resultset is NULL-free
#-
#- the underlying result is fine and contains the right data, just the Python
#- side gets the wrong values
#-
def read_query_result(proxy, inj):
    fields = inj.resultset.fields
    #collectgarbage("collect") #- trigger a full GC
    print '-' * 50, fields

    proxy.response = {
        'type' : proxy.MYSQLD_PACKET_OK,
        'resultset' : {
            'fields' : [],
            'rows' : [],
        }
    }

    proxy.response.resultset.fields.append((fields[0].name, fields[1].type))
    proxy.response.resultset.fields.append((fields[1].name, fields[1].type))
    for row in inj.resultset.rows:
        #collectgarbage("collect") #- trigger a full GC
        #--
        #- if something goes wrong 'row' will reference a free()ed old resultset now
        #- leading to nil here
        proxy.response.resultset.rows.append((row[0], row[1]))

    return proxy.PROXY_SEND_RESULT
