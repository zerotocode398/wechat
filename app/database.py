import sqlite3
from pathlib import Path


DB_FILE = "db.sqlite"


def get_connection():

    conn = sqlite3.connect(DB_FILE)

    conn.row_factory = sqlite3.Row

    return conn


def execute(sql, params=None):
    conn = get_connection()

    cursor = conn.cursor()

    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)

    conn.commit()

    conn.close()


def execute_insert(sql, params=None):
    """Execute INSERT and return lastrowid."""
    conn = get_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id


def fetch_one(sql, params=None):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(sql, params or [])

    result = cursor.fetchone()

    conn.close()

    return result


def fetch_all(sql, params=None):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(sql, params or [])

    result = cursor.fetchall()

    conn.close()

    return result
