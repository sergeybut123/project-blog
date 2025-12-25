from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Post, Comment
from forms import LoginForm, PostForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()


@app.route("/")
def index():
    q = request.args.get("q")
    page = request.args.get("page", 1, type=int)

    query = Post.query
    if q:
        query = query.filter(Post.title.contains(q))

    posts = query.order_by(Post.created.desc()).paginate(page=page, per_page=5)
    return render_template("index.html", posts=posts)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            password=generate_password_hash(request.form["password"])
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("index"))
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/post/create", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("create_post.html", form=form)


@app.route("/post/<int:id>", methods=["GET", "POST"])
def post(id):
    post = Post.query.get_or_404(id)

    if request.method == "POST":
        text = request.form["text"]
        parent_id = request.form.get("parent_id")

        comment = Comment(
            text=text,
            post_id=id,
            parent_id=parent_id if parent_id else None
        )
        db.session.add(comment)
        db.session.commit()

        return redirect(url_for("post", id=id))

    comments = Comment.query.filter_by(post_id=id, parent_id=None).all()
    return render_template("post.html", post=post, comments=comments)

@app.route("/api/posts")
def api_posts():
    posts = Post.query.all()
    return jsonify([
        {"id": p.id, "title": p.title, "content": p.content}
        for p in posts
    ])

@app.route("/post/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)

    if post.author_id != current_user.id:
        return redirect(url_for("index"))

    form = PostForm(obj=post)

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        return redirect(url_for("post", id=id))

    return render_template("create_post.html", form=form)

@app.route("/post/<int:id>/delete", methods=["POST"])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)

    if post.author_id != current_user.id:
        return redirect(url_for("index"))

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)