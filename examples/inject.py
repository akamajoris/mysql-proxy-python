


from proxy_utils import get_query_type, get_query_content


def read_query(proxy, packet):
    query = get_query_content(packet)
    if get_query_type(packet) == proxy.COM_QUERY:
        print 'Got a normal query:', get_query_content(packet)
        proxy.queries.append(1, packet)
        proxy.queries.append(2, chr(proxy.COM_QUERY) + 'select now()', True)
        return proxy.PROXY_SEND_QUERY


def read_query_result(proxy, inj):
    print 'injected result-set id:', inj.id
    if inj.id == 2:
        for r in inj.resultset.rows:
            print 'injected query returned:', r[0]
        return proxy.PROXY_IGNORE_RESULT
