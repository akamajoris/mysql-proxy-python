## A Simple Example ##

Here introduced a very simple example, but contains all the steps to make a  complete python proxy server. This example is derived from the lua script example: log the query time of each sql query statement. First, write our python script query\_time.py, a typical query injection script uses two hook functions.:
```
import proxy_utils as utils

def read_query(proxy, packet):
	if utils.get_query_type(packet) == proxy.COM_QUERY:
		proxy.queries.append(1, packet, False)
		return proxy.PROXY_SEND_QUERY

def read_query_result(proxy, inj):
	print 'query-time:', inj.query_time/1000, 'ms'
	print 'response-time:', inj.response_time/1000, 'ms'
```

This script is quite simple. It contains two hook functions: read\_query(), which is called when the proxy server receives a query from a client, and read\_query\_result(), which is called when the proxy server receives a result of a query from a real mysql server. The code in the tow hook functions is easy to understand. Let's see the import statement first:
```
import proxy_utils as utils
```
When this plugin is loaded at startup of mysql-proxy, tow special path is added to sys.path automatically, one is the path containing the python script, another is `/path/to/mysql-proxy/lib/mysql-proxy/python`, which contains several util modules. "proxy\_utils" is a util module, provide some simple functions to resolve mysql packet.
```
def read_query(proxy, packet):
	if utils.get_query_type(packet) == proxy.COM_QUERY:
		proxy.queries.append(1, packet, False)
		return proxy.PROXY_SEND_QUERY
```
When the client send a query to the proxy server, this function is executed with a "proxy" parameter which contains useful constants and connection specific information, and a "packet" parameter which contains information of the query. First we check if the query type if proxy.COM\_QUERY, that is, a normal "SELECT" statement. If so, we add it to proxy.queries using proxy.queries.append() method, indicates that we want to intercept this query. At last we return proxy.PROXY\_SEND\_QUERY to indicates that the query should be send to the backend server.
```
def read_query_result(proxy, inj):
	print 'query-time:', inj.query_time/1000, 'ms'
	print 'response-time:', inj.response_time/1000, 'ms'
```
When the backend server response the corresponding query result, this read\_query\_result() hook function is executed, with a new "proxy" object as its first parameter and a "inj" object which contains information of this injected query and query its result. We simply print its query-time and response-time. Here we didn't return anything(in fact we returned "None") because different hook function has different action for return nothing, the action of read\_query\_result() is to send the result back to client.

Then start your well-installed mysql-proxy with the following options:
```
    $ mysql-proxy --proxy=pyproxy --pyproxy-backend-addresses=127.0.0.1:3306 --pyproxy-python-script=/path/to/query_time.py &
```

These options indicates mysql-proxy to load pyproxy plugin, proxy with the real mysql server at 127.0.0.1:3306 as the only backend(make sure you have such a mysql server at such an address), listen on 127.0.0.1:4045(by default) as the new address, with the query\_time.py as proxy script.

Now you can start a mysql client to connect to this proxy server:
```
    $ mysql -uxxx -pxxx -h127.0.0.1 -P4045
```

Then you will get the excepted output in the terminal:
```
query-time: 1 ms
response-time: 1 ms
query-time: 2 ms
response-time: 2 ms
query-time: 1 ms
response-time: 1 ms
......
```

You can found more examples of python script in the package, all of them are transplanted from those written in lua.