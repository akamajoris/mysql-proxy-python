pythonextmysqldir = ${libdir}/mysql-proxy/python/mysql
pythonextmysql_LTLIBRARIES = proto.la password.la 

if HAVE_MYSQL_PROXY_SOURCE
pythonextmysql_LTLIBRARIES += tokenizer.la
endif

pythonextmysql_DATA = __init__.py

OBJECT_C=$(srcdir)/../object.c
BUILDLDFLAGS=-module -avoid-version $(PYTHON_LDFLAGS)
BUILDCPPFLAGS=-I$(srcdir)/../ -I$(prefix)/include $(LUA_CFLAGS) $(MYSQL_CFLAGS) $(GLIB_CFLAGS) $(GMODULE_CFLAGS) -pthread $(PYTHON_CFLAGS) -fwrapv -fPIC -Wno-strict-prototypes -Wno-builtin-macro-redefined -shared -Wl,-O1 -Wl,-Bsymbolic-functions

proto_la_SOURCES = proto.c $(OBJECT_C)
proto_la_LDFLAGS = $(BUILDLDFLAGS)
proto_la_CPPFLAGS = $(BUILDCPPFLAGS)


if HAVE_MYSQL_PROXY_SOURCE
tokenizer_la_SOURCES = sql-tokenizer-python.c sql-tokenizer.c sql-tokenizer-tokens.c sql-tokenizer-keywords.c $(OBJECT_C)
tokenizer_la_LDFLAGS = $(BUILDLDFLAGS)
BUILT_SOURCES=sql-tokenizer.c sql-tokenizer-tokens.c sql-tokenizer-keywords.c
tokenizer_la_CPPFLAGS = -I$(MYSQL_PROXY_SOURCE)/lib $(BUILDCPPFLAGS)
endif

sql-tokenizer.c:
	cp $(MYSQL_PROXY_SOURCE)/lib/sql-tokenizer.c $(srcdir)/

sql-tokenizer-tokens.c:
	cp $(MYSQL_PROXY_SOURCE)/lib/sql-tokenizer-tokens.c $(srcdir)/

sql-tokenizer-keywords.c:
	cp $(MYSQL_PROXY_SOURCE)/lib/sql-tokenizer-keywords.c $(srcdir)/


password_la_SOURCES = password.c $(OBJECT_C)
password_la_LDFLAGS = $(BUILDLDFLAGS)
password_la_CPPFLAGS = $(BUILDCPPFLAGS)


__init__.py:
	touch __init__.py
