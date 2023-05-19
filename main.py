from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = TextAreaField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


def add_post_db(title, subtitle, date, body, author, img_url):
    with app.app_context():
        post_to_add = BlogPost()
        post_to_add.title = title
        post_to_add.subtitle = subtitle
        post_to_add.date = date
        post_to_add.body = body
        post_to_add.author = author
        post_to_add.img_url = img_url
        db.session.add(post_to_add)
        db.session.commit()


def update_post_db(post_id, title, subtitle, body, author, img_url):
    with app.app_context():
        post_to_update = BlogPost.query.filter_by(id=post_id).first()

        post_to_update.title = title
        post_to_update.subtitle = subtitle
        post_to_update.body = body
        post_to_update.author = author
        post_to_update.img_url = img_url
        db.session.commit()


def date_now():
    date = datetime.now()
    formatted_date = date.strftime("%B %d, %Y")
    return formatted_date


@app.route('/')
def get_all_posts():
    with app.app_context():
        posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    with app.app_context():
        posts = BlogPost.query.all()
    for blog_post in posts:
        if blog_post.id == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new_post", methods=["GET", "POST"])
def new_post():
    h1 = "New Post"
    blog_post_form = CreatePostForm()
    if blog_post_form.validate_on_submit():
        title = blog_post_form.title.data
        subtitle = blog_post_form.subtitle.data
        date = date_now()
        body = blog_post_form.body.data
        author = blog_post_form.author.data
        img_url = blog_post_form.img_url.data

        add_post_db(title, subtitle, date, body, author, img_url)
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=blog_post_form, h1=h1)


@app.route("/edit_post/<post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    h1 = "Edit Post"
    with app.app_context():
        post = BlogPost.query.filter_by(id=post_id).first()
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )

    if edit_form.validate_on_submit():
        title = edit_form.title.data
        subtitle = edit_form.subtitle.data
        body = edit_form.body.data
        author = edit_form.author.data
        img_url = edit_form.img_url.data

        update_post_db(post_id, title, subtitle, body, author, img_url)
        return redirect(url_for('show_post', index=post_id))

    return render_template("make-post.html", form=edit_form, h1=h1)


@app.route("/delete_post/<int:post_id>")
def delete_post(post_id):
    with app.app_context():
        post_to_delete = BlogPost.query.get(post_id)
        db.session.delete(post_to_delete)
        db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True)
