
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
