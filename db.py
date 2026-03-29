from sqlite3 import Row, connect
from flask import g

def get_connection():
    con = connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = Row
    return con

def execute(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()

def last_insert_id():
    return g.last_insert_id

def query(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result

# TODO: fix me lol
def update_schema():
    try:
        with open("schema.sql") as schema:
            con = get_connection()
            con.executescript(schema.read())
    except Exception as ex:
        print(ex)
