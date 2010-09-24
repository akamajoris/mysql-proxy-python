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


import os, pwd


def read_query (proxy, packet):
    #- ack the packets
    if ord(packet[0]) != proxy.COM_QUERY:
        proxy.response = {
            'type' : proxy.MYSQLD_PACKET_OK
        }
        return proxy.PROXY_SEND_RESULT

    pw = pwd.getpwuid(os.getuid())
    user = 'nil'
    if pw:
        user = pw.pw_name

    proxy.response.type = proxy.MYSQLD_PACKET_OK
    proxy.response.resultset = {
        'fields' : (
            ('user', proxy.MYSQL_TYPE_STRING),
        ),
        'rows' : [[user]]
    }
    return proxy.PROXY_SEND_RESULT
