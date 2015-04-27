## API ##

Tthe api you can use in your python script is almost the same as that in lua, except the

| **hook function** |
|:------------------|
| connect\_server(proxy) |
| read\_handshake(proxy) |
| read\_auth(proxy) |
| read\_auth\_result(proxy, auth) |
| read\_query(proxy, packet) |
| read\_query\_result(proxy, injection) |
| disconnect\_client(proxy) |

These functions are usually module functions. In fact they can be any module-level callable objects as long as they accept the corresponding parameters. These function has exactly the same meaning as those in lua. Please read the document in mysql-proxy package to gain a deeper understanding of mysql client/server communication stages and the behavior of those hook functions.

Now let's explain the common parameter "proxy" of all these functions.

"proxy" object is created each time one of those function is called. It contains some useful constants and all the connection information of the current client. Here list some of the constants:
  * mysql-proxy version: proxy.PROXY\_VERSION
  * hook functions return values
    1. proxy.PROXY\_SEND\_QUERY: indicate proxy send a query to backend server.
    1. proxy.PROXY\_SEND\_RESULT: indicate proxy send a query result to client.
    1. proxy.PROXY\_IGNORE\_RESULT: indicate proxy send nothing to client.
  * query result types
    1. proxy.MYSQLD\_PACKET\_OK: a successful query result, with fields and rows.
    1. proxy.MYSQLD\_PACKET\_ERR: an error result, with error code and message.
    1. proxy.MYSQLD\_PACKET\_RAW: use raw bytes as result.
  * backend mysql server state
    1. proxy.BACKEND\_STATE\_DOWN: the backend server is unavailable.
    1. proxy.BACKEND\_STATE\_UP: the backend server is available.
    1. proxy.BACKEND\_STATE\_UNKNOWN: the backend server'state is unknown.
  * backend mysql server type
    1. proxy.BACKEND\_STATE\_RO: a read only backend server.
    1. proxy.BACKEND\_STATE\_RW: a read write backend server.
    1. proxy.BACKEND\_STATE\_UNKNOWN: the backend server'type is unknown.
  * client query type, here query refers to any packet client sent to server
    1. proxy.COM\_QUERY: a normal "SELECT" statement.
    1. proxy.COM\_QUIT
    1. proxy.COM\_DROP\_DB
    1. proxy.COM\_SHUTDOWN
    1. proxy.COM\_TIME
    1. ...... Detailed information of more query types can be found on mysql protocol page http://forge.mysql.com/wiki/MySQL_Internals_ClientServer_Protocol
  * mysql data type
    1. proxy.MYSQL\_TYPE\_TINY
    1. proxy.MYSQL\_TYPE\_SHORT
    1. proxy.MYSQL\_TYPE\_LONG
    1. proxy.MYSQL\_TYPE\_FLOAT
    1. proxy.MYSQL\_TYPE\_NULL
    1. proxy.MYSQL\_TYPE\_TIMESTAMP
    1. proxy.MYSQL\_TYPE\_DATETIME
    1. proxy.MYSQL\_TYPE\_STRING
    1. ......

Per-connection information of "proxy" object:
  * proxy.connection: