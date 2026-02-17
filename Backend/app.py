from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ---------------- DATABASE CONNECTION ---------------- #

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="student_task_db"
)

cursor = db.cursor(dictionary=True)

# ---------------- AUTH ROUTES ---------------- #

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
    values = (name, email, password)

    try:
        cursor.execute(query, values)
        db.commit()
        return jsonify({"message": "User registered successfully"})
    except:
        return jsonify({"error": "User already exists"}), 400


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    query = "SELECT * FROM users WHERE email=%s AND password=%s"
    cursor.execute(query, (email, password))
    user = cursor.fetchone()

    if user:
        return jsonify({"message": "Login successful", "user_id": user["id"]})
    else:
        return jsonify({"error": "Invalid credentials"}), 401


# ---------------- TASK ROUTES ---------------- #

@app.route('/tasks/<int:user_id>', methods=['GET'])
def get_tasks(user_id):
    query = "SELECT * FROM tasks WHERE user_id=%s ORDER BY created_at DESC"
    cursor.execute(query, (user_id,))
    tasks = cursor.fetchall()
    return jsonify(tasks)


@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.json
    user_id = data.get("user_id")
    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")

    query = """
        INSERT INTO tasks (user_id, title, description, status, due_date, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (user_id, title, description, "pending", due_date, datetime.now())

    cursor.execute(query, values)
    db.commit()

    return jsonify({"message": "Task added successfully"})


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    status = data.get("status")

    query = "UPDATE tasks SET status=%s WHERE id=%s"
    cursor.execute(query, (status, task_id))
    db.commit()

    return jsonify({"message": "Task updated successfully"})


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    query = "DELETE FROM tasks WHERE id=%s"
    cursor.execute(query, (task_id,))
    db.commit()

    return jsonify({"message": "Task deleted successfully"})


# ---------------- RUN SERVER ---------------- #

if __name__ == '__main__':
    app.run(debug=True)

