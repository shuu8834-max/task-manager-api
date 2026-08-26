import datetime
import sqlite3
from flask import Flask, jsonify, request
import jwt

app = Flask(__name__)
app.config["SECRET_KEY"] = "super-secret-key-change-this-in-production"


# 1. Setup relational tables for Users and Tasks
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # User table schema
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """
    )

    # Updated Task table tracking owner relationship via user_id
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """
    )
    conn.commit()
    conn.close()


# 2. Register Route: Create a new account
@app.route("/api/register", methods=["POST"])
def register():
    init_db()
    data = request.get_json()

    if (
        not data
        or "username" not in data
        or "password" not in data
        or not data["username"].strip()
    ):
        return (
            jsonify(
                {"success": False, "error": "Username and password required"}
            ),
            400,
        )

    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (data["username"], data["password"]),
        )
        conn.commit()
        conn.close()
        return (
            jsonify({"success": True, "message": "Account created success!"}),
            201,
        )
    except sqlite3.IntegrityError:
        return (
            jsonify({"success": False, "error": "Username already exists"}),
            400,
        )


# 3. Login Route: Verify credentials and issue a security token
@app.route("/api/login", methods=["POST"])
def login():
    init_db()
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return (
            jsonify({"success": False, "error": "Missing qualifications"}),
            400,
        )

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM users WHERE username = ? AND password = ?",
        (data["username"], data["password"]),
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        return (
            jsonify({"success": False, "error": "Invalid user credentials"}),
            401,
        )

    # Generate a JWT token that expires in 24 hours
    token = jwt.encode(
        {
            "user_id": user[0],  # Plain integer extract
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        },
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )

    # Universal string conversion check for library compatibility
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return (
        jsonify({"success": True, "message": "Logged in!", "token": token}),
        200,
    )


# Helper function to extract user_id from token securely
def get_auth_user():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        # Decode the token
        payload = jwt.decode(
            token, app.config["SECRET_KEY"], algorithms=["HS256"]
        )

        # Universal extraction wrapper to protect against data type variance
        user_data = payload["user_id"]
        if isinstance(user_data, list) or isinstance(user_data, tuple):
            return user_data[0]
        return int(user_data)
    except Exception as e:
        print(f"Token decoding error: {e}")
        return None


# 4. GET: Fetch only the active logged-in user's tasks
@app.route("/api/tasks", methods=["GET"])
def get_user_tasks():
    user_id = get_auth_user()
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized token"}), 401

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, done FROM tasks WHERE user_id = ?", (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    task_list = []
    for row in rows:
        task_list.append({"id": row[0], "title": row[1], "done": bool(row[2])})

    return jsonify({"success": True, "tasks": task_list}), 200


# 5. POST: Link new tasks to the authenticated owner account
@app.route("/api/tasks", methods=["POST"])
def create_user_task():
    user_id = get_auth_user()
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized token"}), 401

    data = request.get_json()
    if not data or "title" not in data or not data["title"].strip():
        return jsonify({"success": False, "error": "Title required"}), 400

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done, user_id) VALUES (?, 0, ?)",
        (data["title"], user_id),
    )
    conn.commit()
    conn.close()

    return (
        jsonify({"success": True, "message": "Task linked to your account!"}),
        201,
    )


if __name__ == "__main__":
    app.run(debug=True)




