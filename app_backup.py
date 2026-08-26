from flask import Flask, jsonify, request,render_template
import sqlite3

app = Flask(__name__)


def get_db():
    connection = sqlite3.connect("tasks.db")
    connection.row_factory = sqlite3.Row
    return connection


connection = get_db()

connection.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0
)
""")

connection.commit()
connection.close()


@app.route("/")
def home():
    return render_template("crome.html")


@app.route("/tasks")
def get_tasks():
    connection = get_db()

    tasks = connection.execute(
        "SELECT * FROM tasks"
    ).fetchall()

    connection.close()

    return jsonify([dict(task) for task in tasks])


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    title = data["title"]

    connection = get_db()

    cursor = connection.execute(
        "INSERT INTO tasks (title) VALUES (?)",
        (title,)
    )

    connection.commit()

    new_id = cursor.lastrowid
    connection.close()

    return jsonify({
        "id": new_id,
        "title": title,
        "completed": False
    }), 201


if __name__ == "__main__":
    app.run()