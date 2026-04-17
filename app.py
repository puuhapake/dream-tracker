from flask import Flask
from flask import render_template, session
from flask import abort, request, redirect

from werkzeug.exceptions import HTTPException
from markupsafe import Markup, escape

import sqlite3
import re

import db
import config
import posts
import users


app = Flask(__name__)
app.secret_key = config.get_session_key()
db.update_schema()

def logged_in() -> bool:
    return "user_id" in session

def check_csrf() -> bool:
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.template_filter()
def show_lines(content):
    content = str(escape(content))
    content = content.replace("\n", "<br />")
    return Markup(content)

@app.route("/")
def index():
    n = config.MAX_PREVIEW_LENGTH
    objs = []

    tab = request.args.get("t", "latest")
    published = posts.get()
    user_id = None

    if logged_in():
        user_id = session["user_id"]

    if tab == "friends" and logged_in():
        published = posts.get_friend_posts(user_id)
    elif tab == "popular":
        published = posts.get_popular_posts()

    for post in published:
        post = dict(post)
        dream = post["dream"] or ""

        if len(dream) > config.MAX_PREVIEW_LENGTH:
            post["preview"] = f"{dream[:n]}..."
        else:
            post["preview"] = dream

        visibility = post["visibility"]
        poster_id = post["user_id"]

        is_poster = is_friend = False

        if logged_in():
            is_poster = user_id == poster_id
            is_friend = users.is_following(poster_id, user_id)

        if visibility == "private" and not is_poster:
            continue
        if visibility == "friends-only" and not (is_poster or is_friend):
            continue

        objs.append(post)
            
    return render_template(
        "index.html", 
        user_count=posts.user_count(),
        post_count=posts.post_count(),
        posts=objs)

@app.route("/user/<username>")
def user_page(username):
    user_id = users.get_id(username)
    user = users.get(user_id) or abort(404, "Ingen användare hittades.")
        
    tab = request.args.get("tab", "posts")
    time = users.join_date(user_id, user["created_at"])

    posts = users.posts(user_id)
    comments = users.get_comments(user_id) if tab == "comments" else None
    likes = users.get_likes(user_id) if tab == "likes" else None

    is_following = False
    if "user_id" in session:
        is_following = users.is_following(
            follower=session["user_id"], 
            target_user=user_id)

    followers = users.get_followers(user_id)

    return render_template(
        "user_page.html", 
        user=user, 
        tab=tab,
        posts=posts,
        time=time,
        likes=likes,
        comments=comments,
        following=is_following,
        followers=followers)

@app.route("/follow/<int:user_id>")
def follow(user_id):
    toggle_follow(user_id, True)
    username = users.get(user_id)["username"]
    return redirect(f"/user/{username}")

@app.route("/unfollow/<int:user_id>")
def unfollow(user_id):
    toggle_follow(user_id, False)
    username = users.get(user_id)["username"]
    return redirect(f"/user/{username}")

def toggle_follow(user_id, toggle):
    if not logged_in():
        abort(403, "Du måste vara inloggad.")

    session_id = session["user_id"]
    if toggle:
        users.follow(session_id, user_id)
    else:
        users.unfollow(session_id, user_id)


@app.route("/post/<int:post_id>")
def display_post(post_id):
    post = posts.get(post_id) or abort(404, "Inlägget hittades inte.")
    visibility = post["visibility"]
    poster_id = post["user_id"]

    user_id = None
    
    # TODO - stronger typing, like enum
    # if visibility == "private" and :
    #     abort(403, "Inlägget är inte tillgängligt.")

    is_liked = False
    is_friend = False
    is_poster = False

    # TODO - recompose to separate function
    if logged_in():
        user_id = session["user_id"]
        is_liked = users.has_liked(user_id, post_id)
        is_poster = user_id == poster_id
        is_friend = users.is_following(poster_id, user_id) or is_poster

    if visibility != "public" and user_id is None:
        abort(403, "Du måste vara inloggad.")
    
    if visibility == "private" and not is_poster:
        abort(403, "Inlägget är inte tillgängligt.")

    if visibility == "friends-only" and not is_friend:
        abort(403, "Inlägget är inte tillgängligt.")

    comments = posts.get_comments(post_id)
    likes = posts.get_likes(post_id)
    quality = sleep_emoticon(post["sleep_quality"])

    return render_template(
        "post.html", 
        post=post, 
        comments=comments,
        is_liked=is_liked,
        likes=likes,
        quality=quality)

def sleep_emoticon(value):
    match int(value):
        case 5:
            return ":D"
        case 4:
            return ":)"
        case 3:
            return ":/"
        case 2:
            return ":("
        case 1:
            return ":C"
        case _:
            return None

@app.route("/draft")
def new_post():
    if not logged_in():
        abort(401, "Du måste vara inloggad.")

    return render_template("draft.html",
        title_max=config.MAX_TITLE_LENGTH,
        dream_max=config.MAX_DREAM_LENGTH)

@app.route("/publish", methods=["POST"])
def publish():
    check_csrf()
    if not logged_in():
        abort(401, "Du måste vara inloggad.")
    
    user_id = session["user_id"]
    title = request.form["title"]
    quality = request.form["sleep_quality"]
    dream = request.form["dream"]

    visibility = request.form["visibility"]
    sleep_type = request.form["type"]

    # bedtime_hour = request.form["bedtime-h"] or 0 
    # bedtime_min = request.form["bedtime-m"] or 0
    bedtime = "00:00"

    # delay_hour = int(request.form["delay-h"]) or 0
    # delay_min = int(request.form["delay-m"]) or 0
    # delay = delay_hour * 60 + delay_min
    delay = 0

    # tags = set()
    # for t in request.form["tags"].split(","):
    #     tags.add(t.strip())

    if len(title) < 1 or len(title) > config.MAX_TITLE_LENGTH:
        abort(403, "Titeln har fel längd")
    if len(dream) > config.MAX_DREAM_LENGTH:
        abort(403, "Texten är för lång")

    posts.add(
        user_id, title, quality, dream,
        visibility, bedtime, delay,
        sleep_type
        )

    return redirect("/")

@app.route("/like", methods=["POST"])
def like():
    check_csrf()
    if not logged_in():
        abort(401, "Du måste vara inloggad.")

    post_id = request.form["post_id"]
    user_id = session["user_id"]
    post = posts.get(post_id) or abort(404, "Inlägget hittades inte.")

    try:
        state = not users.has_liked(user_id, post_id)
        posts.like(post_id, user_id, state=state)
    except sqlite3.IntegrityError as ex:
        print(ex)
        abort(500, "Inlägget har redan gillats.")

    return redirect(f"/post/{post_id}")

@app.route("/comment", methods=["POST"])
def comment():
    check_csrf()
    if not logged_in():
        abort(401, "Du måste vara inloggad.")

    comment = request.form["comment"]
    if len(comment) < 1 or len(comment) > 320:
        abort(403, "Kommentarens längd är fel.")

    user_id = session["user_id"]
    post_id = request.form["post_id"]

    posts.add_comment(post_id, user_id, comment)

    return redirect(f"/post/{post_id}")

@app.route("/edit_post/<int:post_id>")
def edit_post(post_id):
    if not logged_in():
        abort(401, "Du måste vara inloggad.")

    post = posts.get(post_id) or abort(404, "Inlägget hittades inte.")

    if post["user_id"] != session["user_id"]:
        abort(403)

    return render_template("edit_post.html", post=post,
        title_max=config.MAX_TITLE_LENGTH,
        dream_max=config.MAX_DREAM_LENGTH)

@app.route("/edit", methods=["POST"])
def edit():
    check_csrf()
    if not logged_in():
        abort(401, "Du måste vara inloggad.")

    post_id = request.form["post_id"]
    post = posts.get(int(post_id)) or abort(404)

    if post["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    quality = request.form["sleep_quality"]
    dream = request.form["dream"]

    if len(title) < 1 or len(title) > config.MAX_TITLE_LENGTH:
        abort(403, "Titelns längd är fel.")
    if len(dream) > config.MAX_DREAM_LENGTH:
        abort(403, "Texten är för lång.")

    posts.update(post_id, title, quality, dream)
    return redirect(f"post/{post_id}")

@app.route("/delete_post/<int:post_id>", methods=["GET", "POST"])
def delete_post(post_id):
    if not logged_in():
        abort(401, "Du måste vara inloggad.")

    post = posts.get(post_id) or abort(404, "Inlägget hittades inte.")
    if post["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("delete_post.html", post=post)

    if "delete" in request.form:
        check_csrf()
        posts.delete(post_id)
        return redirect("/")

    return redirect(f"/post/{post_id}")

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
        abort(403, "Användarnamnet är för långt.")

    regex = config.USERNAME_RESTRICTION
    if not re.fullmatch(regex, username) or len(username) < 1:
        abort(403, ("FEL: Användarnamnet får inte innehålla"
                    " specialtecken eller mellanslag"))

    if password1 != password2:
        abort(403, "FEL: Lösenord stämmer inte överens")

    if len(password1) < config.MIN_PASSWORD_LENGTH:
        abort(403, "FEL: Lösenordet är för kort")

    try:
        user_id = users.register(username, password1)
    except sqlite3.IntegrityError:
        abort(403, "FEL: Användarnamnet kan inte användas")

    session["user_id"] = user_id 
    session["username"] = username
    session["csrf_token"] = config.csrf_token()
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    result = users.login(username, password)
    if not result:
        abort(403, "Användarnamnet hittades ej.")

    user_id = result["id"]
    password_hash = result["password_hash"]

    if users.authenticate(password_hash, password):
        session["user_id"] = user_id
        session["username"] = username
        session["csrf_token"] = config.csrf_token()
        return redirect("/")

    abort(404, "FEL: Fel användarnamn eller lösenord")

@app.route("/logout")
def logout():
    if logged_in():
        del session["user_id"]
        del session["username"]
    return redirect("/")

@app.errorhandler(HTTPException)
def error_page(e, prev="/"):
    return render_template("error.html", error=e, prev=prev), e.code