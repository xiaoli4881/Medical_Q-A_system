import pymysql
from contextlib import contextmanager
from .config import MYSQL_CONFIG

@contextmanager
def get_db():
    conn = pymysql.connect(**MYSQL_CONFIG)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()