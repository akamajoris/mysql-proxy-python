# LICENSE BEGIN
#
# Copyright (c) 2010 Ysj.Ray
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
## LICENSE END


import sys, os


def parse_arg(name):
    try:
        ind = sys.argv.index('--' + name)
        arg = sys.argv[ind+1]
        del sys.argv[ind:ind+2]
        return arg
    except:
        return ''


src_dir = parse_arg('src_dir')
cflags = parse_arg('cflags')

print '-' * 50, type(cflags), cflags

from distutils.core import setup, Extension
setup(name="pyproxy",
        ext_modules=[
            Extension('chassis', [os.path.join(src_dir, 'chassis.c')],
                extra_compile_args=cflags.split(' ')),
            Extension('glib2', [os.path.join(src_dir, 'glib2.c')]),])
                #extra_compile_args=cflags),
