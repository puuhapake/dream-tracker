from flask import Flask
from flask import render_template, request, redirect, session
import sqlite3

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

import config
import db
import posts

app = Flask(__name__)
app.secret_key = config.get_session_key()
db.update_schema()

@app.route("/")
def index():
    published = posts.get()
    return render_template(
        "index.html", 
        user_count=posts.user_count(),
        post_count=posts.post_count(),
        posts=published)

@app.route("/post/<int:post_id>")
def display_post(post_id):
    post = posts.get(post_id)
    return render_template("display.html", post=post)

@app.route("/draft")
def new_post():
    return render_template("draft.html")

@app.route("/publish", methods=["POST"])
def publish():
    user_id = session["user_id"]
    title = request.form["title"]
    quality = request.form["sleep_quality"]
    dream = request.form["dream"]

    posts.add(user_id, title, quality, dream)

    return redirect("/")

@app.route("/edit_post/<int:pid>")
def edit_post(pid):
    post = posts.get(pid)
    return render_template("edit_post.html", post=post)

@app.route("/edit", methods=["POST"])
def edit():
    pid = request.form["post_id"]
    title = request.form["title"]
    quality = request.form["sleep_quality"]
    dream = request.form["dream"]

    posts.update(pid, title, quality, dream)
    return redirect(f"post/{pid}")

@app.route("/delete_post/<int:pid>", methods=["GET", "POST"])
def delete_post(pid):
    if request.method == "GET":
        post = posts.get(pid)
        return render_template("delete_post.html", post=post)
    
    if "delete" in request.form:
        posts.delete(pid)
        return redirect("/")
    return redirect(f"/post/{pid}")

@app.route("/search")
def search():
    query = request.args.get("q") or ""
    results = posts.find(query) if query else []
    return render_template("search.html", q=query, results=results)

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
    return redirect("/")

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