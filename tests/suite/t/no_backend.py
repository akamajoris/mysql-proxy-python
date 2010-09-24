
def packet_auth(fields={}):
    return "\x0a" +\
        fields.get('version', "5.0.45-proxy") +\
        "\x00" +\
        "\x01\x00\x00\x00" +\
        "\x41\x41\x41\x41" +\
        "\x41\x41\x41\x41" +\
        "\x00" +\
        "\x01\x82" +\
        "\x08" +\
        "\x02\x00" +\
        "\x00" * 13 +\
        "\x41\x41\x41\x41"+\
        "\x41\x41\x41\x41"+\
        "\x41\x41\x41\x41"+\
        "\x00"


#--
#- mock a server
#-
#- don't forward the packets to a back
#-
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
    #- ack the packets
    if ord(packet[0]) != proxy.COM_QUERY:
        proxy.response = {
            'type' : proxy.MYSQLD_PACKET_OK
        }
        return proxy.PROXY_SEND_RESULT

    #- the app query should be discarded
    proxy.queries.append(1, chr(proxy.COM_QUERY) + 'SELECT 1')

    proxy.response = {
        'type' : proxy.MYSQLD_PACKET_OK,
        'resultset' : {
            'fields' : (
                ('1', proxy.MYSQL_TYPE_STRING),
            ),
            'rows' : (
                ( '1', ),
            )
        }
    }

    return proxy.PROXY_SEND_RESULT
