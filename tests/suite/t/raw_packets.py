
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

def connect_server(proxy):
	print 'Now connect server'
	#- emulate a server
	proxy.response = {
		'type' : proxy.MYSQLD_PACKET_RAW,
		'packets' : (
			packet_auth(),
		)
	}
	return proxy.PROXY_SEND_RESULT

def read_query(proxy, packet):
    print 'Now read query:', packet[1:], proxy.connection.backend_ndx
    if ord(packet[0]) == proxy.COM_QUERY:
        q = packet[1:]

        if q == "SELECT 1":
            #- return a empty row
            #-
            proxy.response.type = proxy.MYSQLD_PACKET_RAW
            proxy.response.packets = (
                "\x01",  #- one field
                "\x03def" +\
                  "\x00" +\
                  "\x00" +\
                  "\x00" +\
                  "\x011" +\
                  "\x00" +\
                  "\f" +\
                  "\x08\x00" +\
                  " \x00\x00\x00" +\
                  "\x03" +\
                  "\x02\x00" +\
                  "\x00" +\
                  "\x00\x00",
                "\xfe\x00\x00\x02\x00",
                "\x011",
                "\xfe\x00\x00\x02\x00"
            )

            return proxy.PROXY_SEND_RESULT
        elif q == "SELECT invalid type" :
            #- should be ERR|OK or nil (aka unset)
            proxy.response.type = 25
            #proxy.response.type = proxy.MYSQLD_PACKET_ERR
            proxy.response.errmsg = "I'm a error"
            return proxy.PROXY_SEND_RESULT
        elif q == "SELECT errmsg" :
            #- don't set a errmsg
            proxy.response.type = proxy.MYSQLD_PACKET_ERR
            proxy.response.errmsg = "I'm a error"
            return proxy.PROXY_SEND_RESULT
        elif q == "SELECT errmsg empty" :
            #- don't set a errmsg
            proxy.response.type = proxy.MYSQLD_PACKET_ERR
            return proxy.PROXY_SEND_RESULT
        elif q == "SELECT errcode" :
            #- don't set a errmsg
            proxy.response.type = proxy.MYSQLD_PACKET_ERR
            proxy.response.errmsg = "I'm a error"
            proxy.response.errcode = 1106
            return proxy.PROXY_SEND_RESULT
        else:
            proxy.response = {
                'type' : proxy.MYSQLD_PACKET_ERR,
                'errmsg' : "(raw-packet) unhandled query: " + q
            }
            return proxy.PROXY_SEND_RESULT
    elif ord(packet[0]) == proxy.COM_INIT_DB :
        db = packet[1:]

        proxy.response = {
            'type' : proxy.MYSQLD_PACKET_OK,
            'affected_rows' : 0,
            'insert_id' : 0
        }

        return proxy.PROXY_SEND_RESULT

    proxy.response = {
        'type' : proxy.MYSQLD_PACKET_ERR,
        'errmsg' : "(raw-packet) command " + str(ord(packet[0]))
    }
    return proxy.PROXY_SEND_RESULT
