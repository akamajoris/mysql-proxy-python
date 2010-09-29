SUBDIRS = mysql proxy

pythonextdir = ${libdir}/mysql-proxy/python

pythonext_LTLIBRARIES = chassis.la glib2.la
pythonext_DATA = xtab.py rw_splitting.py admin_sql.py proxy_utils.py


BUILDLDFLAGS=-module -avoid-version $(PYTHON_LDFLAGS) 
BUILDCPPFLAGS=-I$(prefix)/include $(LUA_CFLAGS) $(MYSQL_CFLAGS) $(GLIB_CFLAGS) $(GMODULE_CFLAGS) -pthread $(PYTHON_CFLAGS) -fwrapv -fPIC -Wno-strict-prototypes -Wno-builtin-macro-redefined -shared -Wl,-O1 -Wl,-Bsymbolic-functions


chassis_la_SOURCES = chassis.c
chassis_la_LDFLAGS = $(BUILDLDFLAGS)
chassis_la_CPPFLAGS = $(BUILDCPPFLAGS)


glib2_la_SOURCES = glib2.c
glib2_la_LDFLAGS = $(BUILDLDFLAGS)
glib2_la_CPPFLAGS = $(BUILDCPPFLAGS)

