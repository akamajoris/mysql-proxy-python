
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
