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
    # con.commit()
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
    with open("schema.sql") as schema:
        con = get_connection()
        sql = schema.read() + "\n"
        blocks = sql.split("\n\n")
        
        debug_message("Initializing database tables...")
        for block in blocks:
            try:
                con.executescript(block)
            except OperationalError as ex:
                debug_message(ex, indent=4)

def debug_message(message, indent=2):
    print(f"{' '*indent} > {message}")