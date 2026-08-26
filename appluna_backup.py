import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)


# Database setup helper
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


# 1. GET Endpoints: Fetch all tasks from the database as JSON
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    init_db()  # Ensures database exists
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    # Convert raw database rows into a clean list of Python dictionaries
    task_list = []
    for row in rows:
        task_list.append(
            {
                "id": row[0],
                "title": row[1],
                "done": bool(row[2]),  # Converts 1 to True, 0 to False
            }
        )

    # Return structured JSON response with an HTTP 200 OK status
    return jsonify({"success": True, "tasks": task_list}), 200


# 2. POST Endpoint: Receive JSON data and insert it into the database
@app.route("/api/tasks", methods=["POST"])
def create_task():
    init_db()

    # Read the JSON payload coming from the client
    data = request.get_json()

    # Data Validation: Ensure the client actually sent a title
    if not data or "title" not in data or not data["title"].strip():
        return jsonify({"success": False, "error": "Title is required"}), 400

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, 0)", (data["title"],)
    )
    conn.commit()

    # Get the ID of the task we just inserted
    new_id = cursor.lastrowid
    conn.close()

    # Return the newly created object back to the client with an HTTP 201 Created status
    return (
        jsonify(
            {
                "success": True,
                "message": "Task created successfully",
                "task": {"id": new_id, "title": data["title"], "done": False},
            }
        ),
        201,
    )


if __name__ == "__main__":
    app.run(debug=True)


