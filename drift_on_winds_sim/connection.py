import sqlite3
from sqlite3 import Error

from config import DB_FILE

# === database connexion code ===

def create_connection():
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)

    except Error as e:
        print(e)

    cur = conn.cursor()
    cur.execute("pragma synchronous = off;")
    return conn
