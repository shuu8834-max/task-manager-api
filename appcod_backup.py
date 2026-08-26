import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)


# 1. Setup the Database Table
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0
        )
    """
    )
    conn.commit()
    conn.close()


# 2. GET Route: Fetch all tasks from the database
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    init_db()
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    task_list = []
    for row in rows:
        task_list.append({"id": row[0], "title": row[1], "done": bool(row[2])})

    return jsonify({"success": True, "tasks": task_list}), 200


# 3. POST Route: Add new tasks into the database
@app.route("/api/tasks", methods=["POST"])
def create_task():
    init_db()
    data = request.get_json()

    if not data or "title" not in data or not data["title"].strip():
        return jsonify({"success": False, "error": "Title is required"}), 400

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, 0)", (data["title"],)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return (
        jsonify(
            {
                "success": True,
                "task": {"id": new_id, "title": data["title"], "done": False},
            }
        ),
        201,
    )


if __name__ == "__main__":
    app.run(debug=True)


