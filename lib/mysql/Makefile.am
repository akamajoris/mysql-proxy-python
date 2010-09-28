pythonextmysqldir = ${libdir}/mysql-proxy/python/mysql
pythonextmysql_LTLIBRARIES = proto.la password.la tokenizer.la
pythonextmysql_DATA = __init__.py


proto_la_SOURCES = proto.c $(srcdir)/../object.c
proto_la_LDFLAGS = -module -avoid-version $(PYTHON_LDFLAGS)
proto_la_CPPFLAGS = -I$(srcdir)/../ -I$(prefix)/include $(LUA_CFLAGS) $(MYSQL_CFLAGS) $(GLIB_CFLAGS) $(GMODULE_CFLAGS) -pthread $(PYTHON_CFLAGS) -fwrapv -fPIC -Wno-strict-prototypes -Wno-builtin-macro-redefined -shared -Wl,-O1 -Wl,-Bsymbolic-functions


tokenizer_la_SOURCES = sql-tokenizer-python.c $(srcdir)/../object.c sql-tokenizer.c sql-tokenizer-tokens.c sql-tokenizer-keywords.c
tokenizer_la_LDFLAGS = -module -avoid-version $(PYTHON_LDFLAGS) 
tokenizer_la_CPPFLAGS = -I$(srcdir)/../ -I$(prefix)/include -I$(MYSQL_PROXY_SOURCE)/lib $(LUA_CFLAGS) $(MYSQL_CFLAGS) $(GLIB_CFLAGS) $(GMODULE_CFLAGS) -pthread $(PYTHON_CFLAGS) -fwrapv -fPIC -Wno-strict-prototypes -Wno-builtin-macro-redefined -shared -Wl,-O1 -Wl,-Bsymbolic-functions


password_la_SOURCES = password.c $(srcdir)/../object.c
password_la_LDFLAGS = -module -avoid-version $(PYTHON_LDFLAGS)
password_la_CPPFLAGS = -I$(srcdir)/../ -I$(prefix)/include $(LUA_CFLAGS) $(MYSQL_CFLAGS) $(GLIB_CFLAGS) $(GMODULE_CFLAGS) -pthread $(PYTHON_CFLAGS) -fwrapv -fPIC -Wno-strict-prototypes -Wno-builtin-macro-redefined -shared -Wl,-O1 -Wl,-Bsymbolic-functions


__init__.py:
	touch __init__.py
