pyproxyplugindir = ${libdir}/mysql-proxy/plugins


pyproxyplugin_LTLIBRARIES = libpyproxy.la

libpyproxy_la_LDFLAGS  = -no-undefined -avoid-version -dynamic -Xlinker -export-dynamic $(PYTHON_LDFLAGS)
libpyproxy_la_SOURCES  = pyproxy-plugin.c pyproxy-plugin.h pytypes.c pytypes.h network-mysqld-python.c network-mysqld-python.h
libpyproxy_la_LIBADD   = $(EVENT_LIBS) $(GLIB_LIBS) $(GMODULE_LIBS) $(prefix)/lib/libmysql-proxy.la
libpyproxy_la_CPPFLAGS = -I$(prefix)/include $(MYSQL_CFLAGS) $(GLIB_CFLAGS) $(LUA_CFLAGS) $(GMODULE_CFLAGS) $(PYTHON_CFLAGS) -Wno-strict-prototypes -Wno-builtin-macro-redefined
