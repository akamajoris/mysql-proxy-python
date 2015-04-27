## Basic Usage ##

First of all, you should read the mysql-proxy document to know how to use lua script and get the examples work. The usage of this plugin is almost the same as using lua script in mysql-proxy, except several different configurations and off course, script syntax.

The first thing you should do is make a proper configuration, both in the form of ini file and as command-line options when start up mysql-proxy will be OK. Existing options and their functions of mysql-proxy are not affected. This plugin add several extra options which enables you specify the python script, proxy address, backend address and so on. Details of these options is described in the following paragraph [Differences between lua scripting and python scripting](https://code.google.com/p/mysql-proxy-python/wiki/basic_usage#Differences_between_lua_scripting_and_python_scripting). The most important is, you should add "pyproxy" to option "plugins" to explicitly indicate mysql-proxy load this plugin, like:
```
    plugins=admin,proxy,pyproxy
```

**Note**: the proxy plugin and this pyproxy plugin can be used at the same time!

The following explains some details of differences between lua scripting and python scripting.

## Differences between lua scripting and python scripting ##

#### Configuration ####

Here list extra configuration options provided by this plugin, and corresponding options for lua proxy. As you see, all the option name simply replace "proxy" to "pyproxy". This enables you use lua proxy and python proxy at the same time.

| **Option** | **Meaning** | **Same As** |
|:-----------|:------------|:------------|
| pyproxy-address | listening address:port of proxy server (default: :**4045**), `<host>:<port>` | proxy-address |
| pyproxy-readonly-backend-address | address:port of remote slave-server (default: no set), `<host>:<port>` | proxy-readonly-backend-address |
| pyproxy-backend-addresses | address of remove backend addresses (default: 127.0.0.1:3306), `<host1>:<port1>,<host2>:<port2>...` | proxy-backend-addresses |
| pyproxy-skip-profiling | disable profiling of queries (default: enabled) | proxy-skip-profiling |
| pyproxy-python-script | filename of the python script (default: no set) | proxy-lua-script |
| no-pyproxy | don't start the python proxy plugin (default: enabled) | no-proxy |
| pyproxy-pool-no-change-user | don't use CHANGE\_USER to reset the connection coming from the pool (default: enabled) | proxy-pool-no-change-user |

#### Plugin interface ####

There is few changes in the plugin interface which refers to the several hook functions and object structures. The most obvious one is that you have to explicitly provide the "proxy" parameter as the first parameter of hook functions. In lua the "proxy" parameter is provided implicitly, you need not to write out. Here list the hook functions for python script:

| **hook function** |
|:------------------|
| connect\_server(proxy) |
| read\_handshake(proxy) |
| read\_auth(proxy) |
| read\_auth\_result(proxy, auth) |
| read\_query(proxy, packet) |
| read\_query\_result(proxy, injection) |
| disconnect\_client(proxy) |

There is another difference between the execution of lua script and python script: each time a hook function executes, the lua script is reloaded, the requested lua function is executed, so the local variable defined in lua script is "execution scope". For python, the python script is loaded once at the startup time, then the functions are stored in memory, each time the hook function executes, the stored function is retrieved directly and executed. So the variable defined in python script is "global scope".

Almost all of the classes and names of their data members and methods remain the same, except lua's "proxy.global" becomes python's "proxy.globals" since "global" is a keyword in python.

All the table objects in lua become dict or a kind of object which you can retrive members using '.' syntax. By study the examples you can get details of these changes.