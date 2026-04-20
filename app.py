from flask import Flask
from flask import render_template, session
from flask import abort, request, redirect

from flask import g
from time import time

from werkzeug.exceptions import HTTPException
from markupsafe import Markup, escape

from datetime import datetime
import sqlite3
import re

import db
import config
import posts
import users
import ezformat


app = Flask(__name__)
app.secret_key = config.get_session_key()
db.update_schema()
db.initialize()

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
    content = ezformat.escape(content)

    content = ezformat.set_dashes(content)
    content = ezformat.set_emphs(content)
    content = content.replace("\n", "<br />")

    content = ezformat.unescape(content)
    return Markup(content)

@app.route("/")
def index():
    n = config.MAX_PREVIEW_LENGTH
    limit = config.POST_LIMIT

    page = max(request.args.get("page", 1, type=int), 1)
    print(page)
    offset = (page - 1) * limit

    tab = request.args.get("t", "latest")
    query = request.args.get("q", "").strip() or None

    quality_filter = request.args.get("by_quality", "none")
    if quality_filter == "none":
        quality_filter = None
    else:
        try:
            quality_filter = int(quality_filter)
        except ValueError:
            quality_filter = None
    
    tags = posts.parse_tags(request.args.get("tags", "").strip())

    categories = posts.get_categories()
    cats = {}
    for cat in categories.keys():
        choice = request.args.get(cat)
        if choice:
            cats[cat] = choice

    user_id = session["user_id"] if logged_in() else None

    post_list = posts.get_posts(
        user_id=user_id,
        tab=tab,
        q=query,
        sleep_quality=quality_filter,
        tags=tags,
        cats=cats,
        limit=limit,
        offset=offset
    )

    retrieved = []
    for post in post_list:
        post = dict(post)

        body = post["dream"] or ""

        if len(body) > config.MAX_PREVIEW_LENGTH:
            post["preview"] = f"{body[:n]}..."
        else:
            post["preview"] = body

        retrieved.append(post)

    return render_template(
        "index.html", 
        user_count=posts.user_count(),
        post_count=posts.post_count(),
        posts=retrieved,
        categories=categories)

@app.route("/user/<username>")
def user_page(username):
    user_id = users.get_id(username)
    user = users.get(user_id) or abort(404, config.ERRORS["nouser"])

    tab = request.args.get("tab", "posts")
    time = users.join_date(user_id, user["created_at"])

    viewer_id = None
    if logged_in():
        viewer_id = session["user_id"]

    posts = users.posts(user_id, viewer_id)
    comments = users.get_comments(user_id) if tab == "comments" else None
    liked_posts = users.get_likes(user_id) if tab == "likes" else None

    is_following = False
    if "user_id" in session:
        is_following = users.is_following(
            follower=session["user_id"],
            target_user=user_id)

    followers = users.get_followers(user_id)
    like_count = users.get_like_count(user_id) 

    data = {
        "time": f"Användare sedan {time}",
        "like_count": f"{like_count} likes"
    }

    return render_template(
        "user_page.html", 
        user=user,
        data=data,
        tab=tab,
        posts=posts,
        liked_posts=liked_posts,
        comments=comments,
        followers=followers,
        following=is_following)

@app.route("/follow/<int:user_id>", methods=["POST"])
def follow(user_id):
    check_csrf()
    if not logged_in():
        abort(403, config.ERRORS["login"])

    if user_id == session["user_id"]:
        abort(403, config.ERRORS["generic"])

    users.follow(session["user_id"], user_id)
    username = users.get(user_id)["username"]
    return redirect(f"/user/{username}")

@app.route("/unfollow/<int:user_id>", methods=["POST"])
def unfollow(user_id):
    check_csrf()
    if not logged_in():
        abort(403, config.ERRORS["login"])

    users.unfollow(session["user_id"], user_id)
    username = users.get(user_id)["username"]
    return redirect(f"/user/{username}")

@app.route("/post/<int:post_id>")
def display_post(post_id):
    post = posts.get(post_id) or abort(404, config.ERRORS["nopost"])
    visibility = post["visibility"]
    poster_id = post["user_id"]

    user_id = None

    is_liked = is_friend = is_poster = False

    # TODO - recompose
    if logged_in():
        user_id = session["user_id"]
        is_liked = users.has_liked(user_id, post_id)
        is_poster = user_id == poster_id
        is_friend = users.is_following(poster_id, user_id) or is_poster

    if visibility != "public" and user_id is None:
        abort(403, config.ERRORS["login"])

    if visibility == "private" and not is_poster:
        abort(403, config.ERRORS["unavail"])

    if visibility == "friends-only" and not is_friend:
        abort(403, config.ERRORS["unavail"])

    comments = posts.get_comments(post_id)
    likes = posts.get_likes(post_id)
    quality = ezformat.to_emoticon(post["sleep_quality"])
    tags = posts.get_tags(post_id)
    categories = posts.categorize_dict(post_id)

    bedtime = datetime.strptime(post["bedtime"], "%Y-%m-%dT%H:%M:%S")

    data = {
        "sleep_quality": quality,
        "bedtime": bedtime.strftime("%H:%M")
    }

    return render_template(
        "post.html", 
        post=post,
        comments=comments,
        is_liked=is_liked,
        likes=likes,
        data=data,
        tags=tags,
        categories=categories)

@app.route("/draft")
def new_post():
    if not logged_in():
        abort(401, config.ERRORS["login"])

    return render_template("draft.html",
        categories=posts.get_categories(),
        title_max=config.MAX_TITLE_LENGTH,
        dream_max=config.MAX_DREAM_LENGTH)

@app.route("/publish", methods=["POST"])
def publish():
    check_csrf()
    if not logged_in():
        abort(401, config.ERRORS["login"])

    user_id = session["user_id"]
    title = request.form["title"]
    quality = request.form["sleep_quality"]
    dream = request.form["dream"]

    visibility = request.form["visibility"]

    categories = []
    for c in request.form.getlist("categories"):
        if not c:
            continue
        cat = c.split(":")
        categories.append((cat[0], cat[1]))

    time = datetime.now()
    post_time = time.strftime("%Y-%m-%dT%H:%M:%S")

    bedtime_hour = request.form["bedtime-h"] or 0 
    bedtime_min = request.form["bedtime-m"] or 0
    bedtime = f"{bedtime_hour}:{bedtime_min}"
    bedtime = f"{time.strftime("%Y-%m-%d")}T{bedtime}:00"

    delay_hour = int(request.form["delay-h"]) or 0
    delay_min = int(request.form["delay-m"]) or 0
    delay = delay_hour * 60 + delay_min

    t = request.form["tags"] or ""
    tags = posts.parse_tags(t)

    if len(title) < 1 or len(title) > config.MAX_TITLE_LENGTH:
        abort(403, config.ERRORS["lentitle"])
    if len(dream) > config.MAX_DREAM_LENGTH:
        abort(403, config.ERRORS["lenbody"])

    posts.add(
        user_id, post_time, title, quality,
        dream, visibility, bedtime, delay
        )

    post_id = db.last_insert_id()
    posts.add_tags(post_id, tags)

    posts.update_categories(post_id, categories)

    return redirect("/")

@app.route("/like", methods=["POST"])
def like():
    if not logged_in():
        abort(401, config.ERRORS["login"])
    check_csrf()

    post_id = request.form["post_id"]
    user_id = session["user_id"]
    post = posts.get(post_id) or abort(404, config.ERRORS["nopost"])

    try:
        state = not users.has_liked(user_id, post_id)
        posts.like(post_id, user_id, state=state)
    except sqlite3.IntegrityError as ex:
        print(ex)
        abort(500, config.ERRORS["liked"])

    return redirect(f"/post/{post_id}")

@app.route("/comment", methods=["POST"])
def comment():
    check_csrf()
    if not logged_in():
        abort(401, config.ERRORS["login"])

    comment = request.form["comment"]
    if len(comment) < 1 or len(comment) > 320:
        abort(403, config.ERRORS["lencomm"])

    user_id = session["user_id"]
    post_id = request.form["post_id"]

    posts.add_comment(post_id, user_id, comment)

    return redirect(f"/post/{post_id}")

@app.route("/edit_post/<int:post_id>")
def edit_post(post_id):
    if not logged_in():
        abort(401, config.ERRORS["login"])

    post = posts.get(post_id) or abort(404, config.ERRORS["nopost"])

    if post["user_id"] != session["user_id"]:
        abort(403)

    tags = [tag["tag"] for tag in posts.get_tags(post_id)]
    tags = ", ".join(tags)
    categories = posts.get_categories()

    post_category = dict(posts.categorize_post(post_id))
    bedtime = datetime.strptime(post["bedtime"], "%Y-%m-%dT%H:%M:%S")
    bedtime = (int(bedtime.hour), int(bedtime.minute))

    return render_template("edit_post.html", post=post,
        tags=tags,
        categories=categories,
        bedtime=bedtime,
        post_category=post_category,
        title_max=config.MAX_TITLE_LENGTH,
        dream_max=config.MAX_DREAM_LENGTH)

@app.route("/edit", methods=["POST"])
def edit():
    check_csrf()
    if not logged_in():
        abort(401, config.ERRORS["login"])

    post_id = request.form["post_id"]
    post = posts.get(int(post_id)) or abort(404)

    if post["user_id"] != session["user_id"]:
        abort(403)

    time = datetime.strptime(post["post_time"], "%Y-%m-%dT%H:%M:%S")

    title = request.form["title"]
    quality = request.form["sleep_quality"]
    dream = request.form["dream"]
    visibility = request.form["visibility"]

    tags = set()
    for t in request.form["tags"].split(","):
        if t.strip() == '':
            continue
        tags.add(t.strip())
    tags = list(tags)

    if len(title) < 1 or len(title) > config.MAX_TITLE_LENGTH:
        abort(403, config.ERRORS["lentitle"])
    if len(dream) > config.MAX_DREAM_LENGTH:
        abort(403, config.ERRORS["lenbody"])

    categories = []
    for c in request.form.getlist("categories"):
        if not c:
            continue
        cat = c.split(":")
        categories.append((cat[0], cat[1]))

    bedtime_hour = request.form["bedtime-h"] or 0 
    bedtime_min = request.form["bedtime-m"] or 0
    bedtime = f"{bedtime_hour}:{bedtime_min}"
    bedtime = f"{time.strftime("%Y-%m-%d")}T{bedtime}:00"

    delay_hour = int(request.form["delay-h"]) or 0
    delay_min = int(request.form["delay-m"]) or 0
    delay = delay_hour * 60 + delay_min

    posts.update(post_id, title, quality, dream,
        bedtime, delay, visibility)
    posts.update_categories(post_id, categories)

    posts.delete_tags(post_id)
    posts.add_tags(post_id, tags)

    return redirect(f"post/{post_id}")

@app.route("/delete_post/<int:post_id>", methods=["GET", "POST"])
def delete_post(post_id):
    if not logged_in():
        abort(401, config.ERRORS["login"])

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

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if len(username) > config.MAX_USERNAME_LENGTH:
        abort(403, config.ERRORS["lenuser"])

    regex = config.USERNAME_RESTRICTION
    if not re.fullmatch(regex, username) or len(username) < 1:
        abort(403, config.ERRORS["userspec"])

    if password1 != password2:
        abort(403, config.ERRORS["mismatchpw"])

    if len(password1) < config.MIN_PASSWORD_LENGTH:
        abort(403, config.ERRORS["lenpw"])

    try:
        user_id = users.register(username, password1)
    except sqlite3.IntegrityError:
        abort(403, config.ERRORS["userunavail"])

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
        abort(403, config.ERRORS["nouser"])

    user_id = result["id"]
    password_hash = result["password_hash"]

    if users.authenticate(password_hash, password):
        session["user_id"] = user_id
        session["username"] = username
        session["csrf_token"] = config.csrf_token()
        return redirect("/")

    abort(404, config.ERRORS["auth"])

@app.route("/logout")
def logout():
    if logged_in():
        del session["user_id"]
        del session["username"]
    return redirect("/")

@app.errorhandler(HTTPException)
def error_page(e, prev="/"):
    return render_template("error.html", error=e, prev=prev), e.code

@app.before_request
def before_request():
    g.start_time = time()

@app.after_request
def after_request(response):
    t = round(time() - g.start_time, 2)
    print(f">> Request time: {t} seconds")
    return response
