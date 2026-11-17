import json
from pathlib import Path

from flask import Flask, render_template

app = Flask(__name__)

DATA_FILE = Path(__file__).parent / "blog_posts.json"


def load_posts():
    """Liest alle Blogbeiträge aus der JSON-Datei."""
    with open(DATA_FILE, encoding="utf-8") as file:
        return json.load(file)


@app.route('/')
def index():
    blog_posts = load_posts()
    return render_template('index.html', posts=blog_posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005, debug=True)