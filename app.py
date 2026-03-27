from flask import Flask
from flask import render_template, session
from flask import abort, request, redirect

import sqlite3
import re

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

import config
import db
import posts


app = Flask(__name__)
app.secret_key = config.get_session_key()
db.update_schema()

def logged_in() -> bool:
    return "user_id" in session

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
    post = posts.get(post_id) or abort(404)
    return render_template("display.html", post=post)

@app.route("/draft")
def new_post():
    if not logged_in():
        abort(403)

    return render_template("draft.html",
        title_max=config.MAX_TITLE_LENGTH,
        dream_max=config.MAX_DREAM_LENGTH)

@app.route("/publish", methods=["POST"])
def publish():
    if not logged_in():
        abort(403)
    
    user_id = session["user_id"]
    title = request.form["title"]
    quality = request.form["sleep_quality"]
    dream = request.form["dream"]
    
    if len(title) < 1 or len(title) > config.MAX_TITLE_LENGTH:
        abort(403)
    if len(dream) > config.MAX_DREAM_LENGTH:
        abort(403)

    posts.add(user_id, title, quality, dream)

    return redirect("/")

@app.route("/edit_post/<int:pid>")
def edit_post(pid):
    if not logged_in():
        abort(403)

    post = posts.get(pid) or abort(404)

    if post["uid"] != session["user_id"]:
        abort(403)

    return render_template("edit_post.html", post=post,
        title_max=config.MAX_TITLE_LENGTH,
        dream_max=config.MAX_DREAM_LENGTH)

@app.route("/edit", methods=["POST"])
def edit():
    if not logged_in():
        abort(403)

    pid = request.form["post_id"]
    post = posts.get(int(pid)) or abort(404)

    if post["uid"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    quality = request.form["sleep_quality"]
    dream = request.form["dream"]

    if len(title) < 1 or len(title) > config.MAX_TITLE_LENGTH:
        abort(403)
    if len(dream) > config.MAX_DREAM_LENGTH:
        abort(403)

    posts.update(pid, title, quality, dream)
    return redirect(f"post/{pid}")

@app.route("/delete_post/<int:pid>", methods=["GET", "POST"])
def delete_post(pid):
    if not logged_in():
        abort(403)

    post = posts.get(pid) or abort(404)
    if post["uid"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
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
    
    if len(username) > config.MAX_USERNAME_LENGTH:
        return "FEL: Användarnamnet är för långt"

    regex = config.USERNAME_RESTRICTION
    if not re.fullmatch(regex, username) or len(username) < 1:
        return ("FEL: Användarnamnet får inte innehålla"
                " specialtecken eller mellanslag")

    if password1 != password2:
        return "FEL: Lösenord stämmer inte överens"
    password_hash = generate_password_hash(password1)

    if len(password1) < config.MIN_PASSWORD_LENGTH:
        return "FEL: Lösenordet är för kort"

    try:
        sql = """INSERT INTO Users (username, password_hash)
                 VALUES (?, ?)"""
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "FEL: Användarnamnet kan inte användas"

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
    sql = db.query(query, [username])
    result = sql[0] if sql else None
    if not result:
        abort(404)

    user_id = result["id"]
    password_hash = result["password_hash"]

    if check_password_hash(password_hash, password):
        session["user_id"] = user_id
        session["username"] = username
        return redirect("/")
    else:
        return "FEL: Fel användarnamn eller lösenord"

@app.route("/logout")
def logout():
    if logged_in():
        del session["user_id"]
        del session["username"]
    return redirect("/")