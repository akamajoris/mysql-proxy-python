

from proxy_utils import get_query_type, get_query_content


def connect_server(proxy):
    print 'A client really wants to talk to the server'


def read_handshake(proxy):
    con = proxy.connection
    print "<-- let's send him some information about us"
    print "    mysqld-version: %s" % con.server.mysqld_version
    print "    thread-id     : %s" % con.server.thread_id
    print "    scramble-buf  : %s" % con.server.scramble_buffer
    print "    server-addr   : %s" % con.server.dst.address
    print "    client-addr   : %s" % con.client.src.address

    if con.client.src.address != '127.0.0.1':
        proxy.response.type = proxy.MYSQLD_PACKET_ERR
        proxy.response.errmsg = 'only local connects are allowed'
        print "We don't like this client"
        return proxy.PROXY_SEND_RESULT


def read_auth(proxy):
    con = proxy.connection
    print "--> there, look, the client is responding to the server auth packet"
    print "    username      : %s" % con.client.username
    print "    password      : %s" % con.client.scrambled_password
    print "    default_db    : %s" % con.client.default_db

    if con.client.username == 'evil':
        proxy.response.type = proxy.MYSQLD_PACKET_ERR
        proxy.response.errmsg = 'evil logins are not allowed'
        print "We don't like evil client"
        return proxy.PROXY_SEND_RESULT

def read_auth_result(proxy, auth):
    state = ord(auth[0])
    if state == proxy.MYSQLD_PACKET_OK:
        print '<-- auth ok'
    elif state == proxy.MYSQLD_PACKET_ERR:
        print '<-- auth failed'
    else:
        print '<-- auth dont know:', auth.packet

def read_query(proxy, packet):
    print 'someone send us a query'
    if get_query_type(packet) == proxy.COM_QUERY:
        content = get_query_content(packet)
        print 'query:', content
        if content.upper() == 'SELECT 1':
            print 'add query to inject'
            proxy.queries.append(1, packet, True)
            return proxy.PROXY_SEND_QUERY

def read_query_result(proxy, inj):
    print "<-- ... ok, this only gets called when read_query() told us"
    proxy.response = {
        'type' : proxy.MYSQLD_PACKET_RAW,
        'packets' : '\xff\xff\x04#12S23raw, raw, raw',
        #'errmsg' : 'Cannot select 1',
    }
    return proxy.PROXY_SEND_RESULT
