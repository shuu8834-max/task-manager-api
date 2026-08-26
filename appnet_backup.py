import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

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

if __name__ == "__main__":
    app.run(debug=True)


