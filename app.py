from flask import Flask, render_template, abort
from flask_bootstrap import Bootstrap5
import blog
import pathlib

app = Flask(__name__)
Bootstrap5(app)
BLOG_ROOT = pathlib.Path("blogs")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/projects")
def projects():
    return render_template("projects.html")


@app.route("/leadership")
def leadership():
    return render_template("leadership.html")


@app.route("/blogs")
def blogs():
    return render_template("blogs.html")


@app.route("/blogs/<file_path>")
def article(file_path: str):
    if not file_path.endswith(".md"):
        file_path += ".md"
    file_path = BLOG_ROOT / file_path
    file_path.relative_to(BLOG_ROOT)  # Ensures it's a child
    try:
        payload = blog.render_to_html(file_path)
    except FileNotFoundError:
        return abort(404, "Blog article not found, please return to the home page")
    return render_template("article.html", article=payload)


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run()
