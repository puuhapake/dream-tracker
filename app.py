from flask import Flask
from flask import render_template, request, redirect, session

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

import sqlite3
import config
import db

app = Flask(__name__)
app.secret_key = config.get_session_key()
db.update_schema()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/draft")
def new_post():
    return render_template("draft.html")

@app.route("/publish", methods=["POST"])
def publish():
    user_id = session["user_id"]
    title = request.form["title"]
    quality = request.form["sleep_quality"]
    dream = request.form["dream"]

    db.execute("""
        INSERT INTO Posts (poster_id, title, sleep_quality, dream)
        VALUES (?, ?, ?, ?)
    """, [user_id, title, quality, dream])
    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    
    if password1 != password2:
        return "ERR: Lösenord olika"
    password_hash = generate_password_hash(password1)

    try:
        sql = """INSERT INTO Users (username, password_hash)
                 VALUES (?, ?)"""
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "ERR: Användarnamn upptaget"

    sql = """SELECT id FROM Users WHERE username = ?"""
    user_id = db.query(sql, [username])[0]["id"]

    session["user_id"] = user_id 
    session["username"] = username
    return "Användarkonto skapat"

# @app.route("/error", params?)
# def error(back: str, params: list = []):
#     view render_template("error.html") + params
#     time.sleep(3 seconds)
#     return render_template(back)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    query = "SELECT id, password_hash FROM Users WHERE username = ?"
    sql = db.query(query, [username])[0]
    user_id = sql["id"]
    password_hash = sql["password_hash"]

    if check_password_hash(password_hash, password):
        session["user_id"] = user_id
        session["username"] = username
        return redirect("/")
    else:
        return "ERR: Fel användarnamn eller lösenord"

@app.route("/logout")
def logout():
    try:
        del session["user_id"]
    except Exception as ex:
        print(ex)
    try: 
        del session["username"]
    except Exception as ex:
        print(ex)
    return redirect("/")