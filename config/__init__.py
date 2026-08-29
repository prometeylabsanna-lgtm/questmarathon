"""Project package root.

PyMySQL provides a MySQLdb-compatible API for Hosting Ukraine (no libmysqlclient).
"""

try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    pass
