from sqlite3 import Row, connect, OperationalError
from flask import g

def get_connection():
    con = connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = Row
    return con

def execute(sql, params=[]):
    con = get_connection()
    with con:
        result = con.execute(sql, params)
    g.last_insert_id = result.lastrowid
    con.close()

def executemany(sql, params=[]):
    con = get_connection()
    with con:
        result = con.executemany(sql, params)
    g.last_insert_id = result.lastrowid
    con.close()

def last_insert_id():
    return g.last_insert_id

def query(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result

def update_schema():
    debug_message("Initializing database tables...")
    con = get_connection()

    for block in open_sql("schema.sql"):
        try:
            con.executescript(block)
        except OperationalError as ex:
            debug_message(ex, indent=4)
    
def initialize():
    con = get_connection()
    for block in open_sql("init.sql"):
        try:
            con.executescript(block)
        except OperationalError as ex:
            debug_message(ex, indent=4)

def open_sql(filename):
    with open(filename, encoding="utf-8") as sql_file:
        sql = sql_file.read() + "\n"
        return sql.split("\n\n")


def debug_message(message, indent=2):
    print(f"{' '*indent} > {message}")