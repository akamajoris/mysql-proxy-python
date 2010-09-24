

from distutils.core import setup, Extension

setup(name="pyproxy",
        ext_modules=[
            Extension('chassis', ['chassis.c'],),
            Extension('glib2', ['glib2.c']),
            Extension('mysql.proto', ['mysql-proto.c']),])
