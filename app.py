import json
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

DATA_FILE = Path(__file__).parent / "blog_posts.json"


def load_posts():
    """Liest alle Blogbeiträge aus der JSON-Datei."""
    with open(DATA_FILE, encoding="utf-8") as file:
        return json.load(file)


def save_posts(posts):
    """Schreibt die komplette Liste zurück in die JSON-Datei."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(posts, file, indent=4, ensure_ascii=False)


def next_id(posts):
    """Nächste freie ID: höchste vorhandene ID + 1 (bei leerer Liste 1)."""
    return max((post["id"] for post in posts), default=0) + 1


@app.route('/')
def index():
    blog_posts = load_posts()
    return render_template('index.html', posts=blog_posts)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        author = request.form.get('author', '').strip()
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()

        # Server prüft selbst – "required" im Formular reicht nicht
        if not author or not title or not content:
            return render_template('add.html', error="Bitte alle Felder ausfüllen.",
                                   author=author, title=title, content=content)

        blog_posts = load_posts()
        blog_posts.append({
            "id": next_id(blog_posts),
            "author": author,
            "title": title,
            "content": content,
        })
        save_posts(blog_posts)
        return redirect(url_for('index'))

    return render_template('add.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005, debug=True)