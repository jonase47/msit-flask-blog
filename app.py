import json
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)

DATA_FILE = Path(__file__).parent / "blog_posts.json"
FORM_FIELDS = ("author", "title", "content")


def load_posts():
    """Liest alle Blogbeiträge aus der JSON-Datei (fehlt sie, leere Liste)."""
    try:
        with open(DATA_FILE, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_posts(posts):
    """Schreibt die komplette Liste zurück in die JSON-Datei."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(posts, file, indent=4, ensure_ascii=False)


def next_id(posts):
    """Nächste freie ID: höchste vorhandene ID + 1 (bei leerer Liste 1)."""
    return max((post["id"] for post in posts), default=0) + 1


def fetch_post_by_id(posts, post_id):
    """Sucht in einer bereits geladenen Liste den Beitrag mit post_id (sonst None)."""
    return next((post for post in posts if post["id"] == post_id), None)


def read_post_form():
    """Liest Autor, Titel und Inhalt aus dem Formular und prüft sie serverseitig.

    Gibt (daten, fehler) zurück: daten enthält die getrimmten Werte,
    fehler ist None oder eine Meldung, wenn ein Feld leer ist.
    """
    data = {field: request.form.get(field, "").strip() for field in FORM_FIELDS}
    # Server prüft selbst – "required" im Formular reicht nicht
    if not all(data.values()):
        return data, "Bitte alle Felder ausfüllen."
    return data, None


@app.route('/')
def index():
    """Zeigt alle Blogbeiträge."""
    return render_template('index.html', posts=load_posts())


@app.route('/add', methods=['GET', 'POST'])
def add():
    """Zeigt das Formular (GET) bzw. legt einen neuen Beitrag an (POST)."""
    if request.method == 'POST':
        data, error = read_post_form()
        if error:
            return render_template('add.html', error=error, **data)

        blog_posts = load_posts()
        blog_posts.append({"id": next_id(blog_posts), **data, "likes": 0})
        save_posts(blog_posts)
        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/delete/<int:post_id>', methods=['POST'])
def delete(post_id):
    """Löscht den Beitrag mit post_id; unbekannte ID ergibt 404."""
    blog_posts = load_posts()
    remaining = [post for post in blog_posts if post["id"] != post_id]

    if len(remaining) == len(blog_posts):   # nichts entfernt → ID gibt es nicht
        abort(404)

    save_posts(remaining)
    return redirect(url_for('index'))


@app.route('/update/<int:post_id>', methods=['GET', 'POST'])
def update(post_id):
    """Zeigt das Bearbeitungsformular (GET) bzw. speichert die Änderungen (POST)."""
    blog_posts = load_posts()
    post = fetch_post_by_id(blog_posts, post_id)
    if post is None:
        abort(404)

    if request.method == 'POST':
        data, error = read_post_form()
        if error:
            # eingegebene Werte zurück ins Formular, gespeichert wird nichts
            return render_template('update.html', error=error,
                                   post={"id": post_id, **data})

        post.update(data)
        save_posts(blog_posts)
        return redirect(url_for('index'))

    return render_template('update.html', post=post)


@app.route('/like/<int:post_id>', methods=['POST'])
def like(post_id):
    """Erhöht die Likes des Beitrags mit post_id um eins."""
    blog_posts = load_posts()
    post = fetch_post_by_id(blog_posts, post_id)
    if post is None:
        abort(404)

    post["likes"] = post.get("likes", 0) + 1
    save_posts(blog_posts)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
