from flask import Blueprint, render_template, redirect, request, flash, session
from .db import *
from .send_email import Email
from random import randint
from urllib.parse import unquote
import hashlib

users_path = 'users.json'

view = Blueprint('view', __name__)
users = create_db(users_path)
admins = [
    "MrPsyghost",
    "Tanishq",
]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@view.route('/')
def home():
    global users
    return render_template("index.html", users=users)

@view.route('/signup', methods=['GET', 'POST'])
def signup():
    global users

    if request.method == 'POST' and session.get("verification"):
        entered_code = request.form.get("code")

        if entered_code != session.get("verification"):
            flash("Invalid verification code.", "error")
            return redirect("/signup")

        pending = session.get("pending_user")

        create_user(
            users,
            pending["username"],
            pending["email"],
            hash_password(pending["password"])
        )

        save_db(users_path, users)

        Email(
            pending["email"],
            "Account Successfully created on StackAI!",
            "Thanks for signing up into StackAI. You'll now be updated when you get either a reply or a comment."
        )

        session['user'] = pending['username']
        session.pop("verification", None)
        session.pop("pending_user", None)
        
        return redirect("/")

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if username in users:
            flash("Error: User already exists.", category="info")
            Email(
                email,
                "Error: Username already taken",
                f"We're sorry but the username '{username}' you chose is already taken on StackAI."
            )
            return redirect("/signup")

        code = str(randint(100000, 999999))

        session["verification"] = code
        session["pending_user"] = {
            "username": username,
            "email": email,
            "password": password
        }

        Email(
            email,
            "Account Verification!",
            f"Your StackAI verification code is: {code}"
        )

        return redirect("/signup")

    return render_template("signup.html", users=users)

@view.route('/login', methods=['GET', 'POST'])
def login():
    global users
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username.lower() in lower_all(list(users.keys())):
            if hash_password(password) == users[username]["credentials"]["password"]:
                session.permanent = True
                session["user"] = username
                return redirect("/")
            Email(users[username]["credentials"]["email"], 'Someone tried to login using your email!', 'Someone just tried to login into your account using your email but failed at guessing the correct password.')
        return redirect('/login')
    return render_template("login.html", users=users)

@view.route('/report', methods=['GET', 'POST'])
def report():
    global users
    if request.method == 'POST':
        try:
            username = session['user']
            ai = request.form.get('ai')
            sub = request.form.get('sub')
            desc = request.form.get('desc')
            if not ai:
                return redirect('/report')
            report = add_report(users, username, ai, sub, desc)
            if not report:
                return redirect('/report')
            save_db(users_path, users)

            return redirect('/forum')
        except:
            return redirect('/login')
    return render_template("report.html", users=users)

@view.route('/forum')
def forum():
    global users, admins
    reports = read_db(users)
    return render_template("forum.html", reports=reports, admins=admins, users=users)

@view.route("/logout")
def logout():
    session.pop("user", None)
    session.permanent = False
    return redirect('/')

@view.route('/delete-post', methods=['POST'])
def delete_post():
    global users

    if "user" not in session:
        return {"error": "unauthorized"}, 401

    data = request.get_json()
    subject = data.get("subject")

    username = session["user"]

    if username in users and subject in users[username]["posts"]:
        del users[username]["posts"][subject]
        save_db(users_path, users)
        return {"status": "ok"}

    return {"error": "not found"}, 404

@view.route('/post/<username>/<subject>')
def view_post(username, subject):
    global users

    if username.lower() not in lower_all(list(users.keys())):
        return redirect("/forum")

    posts = users[username]["posts"]

    if subject not in posts:
        return redirect("/forum")

    post = posts[subject]
    comments = post["comments"]

    return render_template(
        "post.html",
        username=username,
        subject=subject,
        ai=post["ai"],
        desc=post["desc"],
        comments=comments,
        users=users
    )

@view.route('/post/<username>/<subject>', methods=['GET', 'POST'])
def post(username, subject):
    global users

    subject = unquote(subject)

    if username not in users:
        return redirect("/forum")

    posts = users[username]["posts"]

    if subject not in posts:
        return redirect("/forum")

    if request.method == "POST":
        if "user" not in session:
            return redirect("/login")

        text = request.form.get("comment")

        if text:
            add_comment(users, username, subject, session.get('user'), text)
            save_db(users_path, users)

        return redirect(f"/post/{username}/{subject}")

    post = posts[subject]

    return render_template(
        "post.html",
        username=username,
        subject=subject,
        ai=post["ai"],
        desc=post["desc"],
        comments=post["comments"],
        users=users
    )

@view.route('/delete-comment', methods=['POST'])
def delete_comment():
    global users

    if "user" not in session:
        return {"error": "unauthorized"}, 401

    data = request.get_json()
    post_owner = data.get("post_owner")
    subject = unquote(data.get("subject"))
    index = data.get("index")

    if post_owner not in users:
        return {"error": "post owner not found"}, 404

    posts = users[post_owner]["posts"]

    if subject not in posts:
        return {"error": "post not found"}, 404

    comments = posts[subject]["comments"]

    if not isinstance(index, int) or index < 0 or index >= len(comments):
        return {"error": "invalid comment index"}, 400
    
    if comments[index]["user"] != session["user"]:
        return {"error": "forbidden"}, 403

    del comments[index]
    save_db(users_path, users)

    return {"status": "ok"}