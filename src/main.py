# Import your forms from the forms.py
from forms import (
    CreatePostForm,
    RegisterForm,
    LoginForm,
    RegisterUserData,
    LoginData,
    CommentForm,
    CommentData,
)
from models import BlogPost, User, db, Comment
from helpers import user_exists, is_safe

from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import login_user, LoginManager, current_user, logout_user
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import string

load_dotenv()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
ckeditor = CKEditor(app)
Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id) -> User | None:
    return db.session.get(User, user_id)


database_url = os.getenv("POSTGRES_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_data: RegisterUserData = form.get_data()
        if user_exists(db=db, email=user_data.email):
            flash("Email exists. Please login instead")
            return redirect(url_for("login"))

        hashed_password: str = generate_password_hash(
            password=user_data.password, method="pbkdf2:sha256", salt_length=8
        )
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            password=hashed_password,
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        next_page = request.args.get("next")
        if next_page and is_safe(next_page):
            return redirect(next_page)
        return redirect(url_for("get_all_posts"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_data: LoginData = form.get_data()
        user = user_exists(db, user_data.email)
        if user:
            if check_password_hash(user.password, user_data.password):
                login_user(user)

                next_page = request.args.get("next")
                if next_page and is_safe(next_page):
                    return redirect(next_page)
                return redirect(url_for("get_all_posts"))
            else:
                flash("Password incorect")
        else:
            flash("That email does not exist. Please try again")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = CommentForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            comment_data: CommentData = form.get_data()
            new_comment = Comment(
                text=comment_data.comment,
                author_id=current_user.id,
                post_id=requested_post.id,
            )
            db.session.add(new_comment)
            db.session.commit()
            return render_template("post.html", post=requested_post, form=form)
        else:
            flash("Must be signed in to comment")
            return redirect(url_for("login"))
    return render_template("post.html", post=requested_post, form=form)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author_id=current_user.id,
            date=date.today().strftime("%B %d, %Y"),
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body,
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=False, port=5002)
