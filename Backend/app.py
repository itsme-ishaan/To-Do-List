from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import mysql.connector
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Session ke liye
CORS(app)

# ---------------- DATABASE CONNECTION ---------------- #
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Uni#21que",
        database="student_task_db",
        autocommit=True
    )

# ---------------- LOGIN REQUIRED DECORATOR ---------------- #
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- FRONTEND ROUTES ---------------- #
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', 
                         user_name=session.get('user_name'),
                         user_id=session.get('user_id'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ---------------- AUTH API ROUTES ---------------- #
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
    values = (name, email, password)

    try:
        cursor.execute(query, values)
        cursor.close()
        db.close()
        return jsonify({"message": "User registered successfully", "success": True})
    except Exception as e:
        return jsonify({"error": "User already exists", "success": False}), 400


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE email=%s AND password=%s"
    cursor.execute(query, (email, password))
    user = cursor.fetchone()
    
    cursor.close()
    db.close()

    if user:
        # Session mein store karo
        session['user_id'] = user["id"]
        session['user_name'] = user["name"]
        
        return jsonify({
            "message": "Login successful", 
            "user_id": user["id"],
            "name": user["name"],
            "success": True
        })
    else:
        return jsonify({"error": "Invalid credentials", "success": False}), 401


# ---------------- TASK API ROUTES ---------------- #
@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    user_id = session.get('user_id')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT * FROM tasks WHERE user_id=%s ORDER BY created_at DESC"
    cursor.execute(query, (user_id,))
    tasks = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return jsonify(tasks)


@app.route('/api/tasks', methods=['POST'])
@login_required
def add_task():
    data = request.json
    user_id = session.get('user_id')
    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")
    priority = data.get("priority", "medium")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = """
        INSERT INTO tasks (user_id, title, description, status, due_date, priority, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (user_id, title, description, "pending", due_date, priority, datetime.now())

    cursor.execute(query, values)
    task_id = cursor.lastrowid
    
    cursor.close()
    db.close()

    return jsonify({"message": "Task added successfully", "task_id": task_id, "success": True})


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    data = request.json
    status = data.get("status")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = "UPDATE tasks SET status=%s WHERE id=%s AND user_id=%s"
    cursor.execute(query, (status, task_id, session.get('user_id')))
    
    cursor.close()
    db.close()

    return jsonify({"message": "Task updated successfully", "success": True})


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = "DELETE FROM tasks WHERE id=%s AND user_id=%s"
    cursor.execute(query, (task_id, session.get('user_id')))
    
    cursor.close()
    db.close()

    return jsonify({"message": "Task deleted successfully", "success": True})


if __name__ == '__main__':
    app.run(debug=True, port=5000)