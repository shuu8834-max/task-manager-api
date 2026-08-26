import sqlite3
from flask import Flask, redirect, request, url_for

app = Flask(__name__)


# This function handles the automated database setup
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
    # Put default tasks in if table is brand new
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone() == 0:
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES ('Learn Flask', 0)"
        )
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES ('Practice Python', 1)"
        )
    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def home():
    # CRITICAL FIX: Run database setup immediately when the user visits the page
    init_db()

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        new_task = request.form["task"]
        if new_task.strip():
            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES (?, 0)", (new_task,)
            )
            conn.commit()
        conn.close()
        return redirect(url_for("home"))

    cursor.execute("SELECT title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    task_list = ""
    for row in rows:
        title = row[0]
        done = row[1]
        status = "✅" if done == 1 else "❌"
        task_list += f"<li>{title} {status}</li>"

    return f"""
    <h1>My Task Manager (With Database)</h1>
    <p>Your tasks are now permanently saved in database.db!</p>

    <h2>My Tasks</h2>

    <form method="post">
        <input type="text" name="task" placeholder="Enter a task" required>
        <button type="submit">Add Task</button>
    </form>

    <ul>
        {task_list}
    </ul>
    """


if __name__ == "__main__":
    app.run(debug=True)

