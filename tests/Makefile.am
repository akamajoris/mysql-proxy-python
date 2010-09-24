
TESTS_ENVIRONMENT = \
    MYSQL_TEST_BIN="${MYSQL_TEST_BIN}" \
    LUA_USER_PATH="${prefix}/lib/mysql-proxy/lua/proxy/?.lua" \
    LUA_CPATH="${prefix}/lib/mysql-proxy/lua/?.@DYNLIB_LUA_SUFFIX@" \
    @DYNLIB_PATH_VAR@="${top_builddir}/src/.libs/:${@DYNLIB_PATH_VAR@}" \
    MYSQL_PROXY_VERSION="${PACKAGE_VERSION}" \
	PROXY_BINPATH="${prefix}/bin/mysql-proxy" \
	PROXY_LIBPATH="${prefix}/lib/mysql-proxy/plugins" \
	PYTHON_LIBPATH="${prefix}/lib/mysql-proxy/python" \
    top_builddir=${top_builddir} \
    builddir=${builddir} \
    srcdir=${srcdir}/ \
    BUILD_OS=${build} \
	${srcdir}/run-tests.lua


TESTS=suite
