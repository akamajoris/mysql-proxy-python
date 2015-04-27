## Installation ##

#### Requirements ####
  * autotools
  * python2.5 package or latter, but not python3.x.
  * python2.x-dev package.
  * python2.x-config script, usually it's installed with python2.5 dpkg package. This script is to fetch python informations like compiling include directories and ld flags. If your python is not installed through that way, you'd better write one yourself.
  * mysql-proxy-0.8.0 installed. For information about how to install mysql-proxy-0.8.0,  see mysql-proxy documents. You should have a successful installation and get the example work.

#### To install from source ####
> Visit https://code.google.com/p/mysql-proxy-python/downloads/list and choice one, then execute the following commands:
```
        $ ls
        mysql-proxy-python-0.8.0.tar.gz
        $ tar xvf mysql-proxy-python-0.8.0.tar.gz
        $ cd mysql-proxy-python-0.8.0
        $ ./configure --with-python=python2.5 --prefix=/path/to/mysql-proxy/
        $ make 
        $ make install
```
> After installation, you can run "make check" optionally to check for installation.

#### To install from repository(latest version) ####
> First, checkout the source from svn:
```
        $ svn checkout http://mysql-proxy-python.googlecode.com/svn/trunk/ mysql-proxy-python
```
> Then using the configure & make procedure:
```
        $ cd mysql-proxy-python
        $ autoreconf -fvi
        $ ./configure --with-python=python2.5 --prefix=/path/to/mysql-proxy/
        $ make 
        $ make install
```