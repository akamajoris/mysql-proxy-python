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

print sys.path

import proxy.tokenizer as tk

DEBUG = os.getenv('DEBUG') or 0
DEBUG=DEBUG+0

def print_debug(msg):
    if DEBUG > 0:
        print msg

def packet_auth(fields = {}):
    return "\x0a" +\
        fields.get('version', "5.0.45-proxy") +\
        "\x00" +\
        "\x01\x00\x00\x00" +\
        "\x41\x41\x41\x41" +\
        "\x41\x41\x41\x41" +\
        "\000" +             \
        "\x01\x82" +         \
        "\x08" +             \
        "\x02\x00" +         \
        "\x00"*13 +   \
        "\x41\x41\x41\x41"+\
        "\x41\x41\x41\x41"+\
        "\x41\x41\x41\x41"+\
        "\x00"

def connect_server(proxy):
	#- emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (
			packet_auth(),
		)
	}
	return proxy.PROXY_SEND_RESULT


def read_query(proxy, packet):
    if ord(packet[0]) != proxy.COM_QUERY:
        print_debug('>>>>>> skipping')
        proxy.response = { 'type' : proxy.MYSQLD_PACKET_OK }
        return proxy.PROXY_SEND_RESULT
    print_debug('>>>>>> after skipping')
    query = packet[1:]
    tokens = tk.tokenize(query)
    stripped_tokens = tk.tokens_without_comments(tokens)
    simple_tokens = tk.bare_tokens(stripped_tokens, True)
    proxy.response.type = proxy.MYSQLD_PACKET_OK
    proxy.response.resultset = {
        'fields' : (
            ('item', proxy.MYSQL_TYPE_STRING),
            ('value', proxy.MYSQL_TYPE_STRING),
        ),
        'rows' : (
            ( 'original', query ),
            ( 'rebuilt', tk.tokens_to_query(tokens) )
        )
    }

    print_debug('>>>>>> returning')
    return proxy.PROXY_SEND_RESULT

def disconnect_client(proxy):
	print_debug('>>>>>> end session')
