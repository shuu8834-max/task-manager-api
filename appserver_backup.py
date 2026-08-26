import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)


# 1. Automated Table Setup
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


# 2. GET Route: Fetch data cleanly
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
        # Explicit index mapping ensures your data parses cleanly to JSON
        task_list.append(
            {"id": row[0], "title": row[1], "done": bool(row[2])}
        )

    return jsonify({"success": True, "tasks": task_list}), 200


# 3. POST Route: Accept items
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


# 4. PUT Route: Change status
@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    if not data or "done" not in data:
        return (
            jsonify({"success": False, "error": "Missing 'done' field"}),
            400,
        )

    done_val = 1 if data["done"] else 0

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET done = ? WHERE id = ?", (done_val, task_id)
    )
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"success": False, "error": "Task not found"}), 404

    conn.close()
    return (
        jsonify(
            {"success": True, "message": f"Task {task_id} status updated"}
        ),
        200,
    )


# 5. DELETE Route: Remove data items
@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"success": False, "error": "Task not found"}), 404

    conn.close()
    return (
        jsonify({"success": True, "message": f"Task {task_id} deleted"}),
        200,
    )


if __name__ == "__main__":
    app.run(debug=True)




