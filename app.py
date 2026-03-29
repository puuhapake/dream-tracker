from flask import Flask
from flask import render_template, session
from flask import abort, request, redirect

import sqlite3
import re

import db
import config
import posts
import users
# import auth


app = Flask(__name__)
app.secret_key = config.get_session_key()
db.update_schema()

# pylint: disable=W0105
'''Planned actions

- Refactor code + write docs
- Posts to front page (home + following feed)
- Search bar to front page
- Likes and comments
- Follow users, subscribing to their feeds
- Sort by New / Popular (number of likes) / Friends
- Set post(s) as public, private or friends-only
- User-defined (hash?)tags for posts
- Wider user- and post-specific statistics
- List collections, e.g. "Premonitions", "Nightmares", 
    "Sleepover", "Memories" et cetera
''' # pylint: enable=W0105

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

@app.route("/user/<int:uid>")
def user_page(uid):
    user = users.get(uid) or abort(404)
    posts = users.posts(uid)
    time = users.join_date(uid, user["created_at"])
    return render_template(
        "user_page.html", 
        user=user, 
        posts=posts,
        time=time)

@app.route("/post/<int:post_id>")
def display_post(post_id):
    post = posts.get(post_id) or abort(404)
    return render_template("post.html", post=post)

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
    quality_filter = request.args.get("by_quality")
    if quality_filter == "none":
        quality_filter = ""

    query = request.args.get("q") or ""
    if query or quality_filter:
        results = posts.find(query, quality_filter)
    else:
        results = []
    print(results)
    return render_template("search.html", 
        q=query, 
        filter=quality_filter,
        results=results)

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

    if len(password1) < config.MIN_PASSWORD_LENGTH:
        return "FEL: Lösenordet är för kort"

    try:
        user_id = users.register(username, password1)
    except sqlite3.IntegrityError:
        return "FEL: Användarnamnet kan inte användas"

    session["user_id"] = user_id 
    session["username"] = username
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    result = users.login(username, password)
    if not result:
        abort(403)

    user_id = result["id"]
    password_hash = result["password_hash"]

    if users.authenticate(password_hash, password):
        session["user_id"] = user_id
        session["username"] = username
        return redirect("/")

    return "FEL: Fel användarnamn eller lösenord"

@app.route("/logout")
def logout():
    if logged_in():
        del session["user_id"]
        del session["username"]
    return redirect("/")
