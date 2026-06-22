import pymysql
import os
from urllib.parse import urlparse
from dbutils.pooled_db import PooledDB

pool = None

def init_db_pool():
    global pool
    db_url = os.environ.get("MYSQL_URL")
    if db_url:
        parsed = urlparse(db_url)
        pool = PooledDB(
            creator=pymysql,
            maxconnections=20,
            mincached=2,
            maxcached=5,
            blocking=True,
            host=parsed.hostname,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:],
            port=parsed.port or 3306,
            cursorclass=pymysql.cursors.DictCursor
        )
    else:
        pool = PooledDB(
            creator=pymysql,
            maxconnections=20,
            mincached=2,
            maxcached=5,
            blocking=True,
            host=os.environ.get("MYSQLHOST", "localhost"),
            user=os.environ.get("MYSQLUSER", "root"),
            password=os.environ.get("MYSQLPASSWORD") or os.environ.get("MYSQL_PASSWORD", ""),
            database=os.environ.get("MYSQLDATABASE", "idx_screener"),
            port=int(os.environ.get("MYSQLPORT", 3306)),
            cursorclass=pymysql.cursors.DictCursor
        )

def get_db_connection():
    global pool
    if pool is None:
        init_db_pool()
    return pool.connection()
