from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import mysql.connector
from datetime import datetime
from functools import wraps
import os

# --- NAYA SDK IMPORT KIYA HAI ---
from google import genai

app = Flask(__name__)

# Security & Session Configuration
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_taskflow_2026')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=600 # 10 minutes
)

CORS(app, supports_credentials=True)

# ---------------- AI CHATBOT SETUP (NAYA SDK) ---------------- #
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyA18noY3O9rI6OFclhi-bxuTghn0riqK2M')

try:
    # Naye package me setup is tarah hota hai
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"AI Setup Error: {e}")
    ai_client = None

# ---------------- DATABASE CONNECTION ---------------- #
def get_db():
    try:
        return mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASS', 'Uni#21que'),
            database=os.environ.get('DB_NAME', 'student_task_db'),
            autocommit=True
        )
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# ---------------- LOGIN REQUIRED DECORATOR ---------------- #
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({"error": "Unauthorized"}), 401
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
    subjects = [
        "Advanced Java", "Competitive Coding - II", 
        "Advanced SE and Agile Practises", "Cloud Computing", 
        "Applied System Design", "Minor Project", "Generative AI"
    ]
    return render_template('dashboard.html', 
                         user_name=session.get('user_name'),
                         user_id=session.get('user_id'),
                         role=session.get('role'),
                         subjects=subjects)

# Naya Analytics Page Route
@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html', 
                         user_name=session.get('user_name'),
                         role=session.get('role'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ---------------- AUTH API ROUTES ---------------- #
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    db = get_db()
    if not db: return jsonify({"error": "Database connection failed"}), 500
    
    cursor = db.cursor(dictionary=True)
    try:
        query = "SELECT id, name, role FROM users WHERE email=%s AND password=%s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        
        if user:
            session.permanent = True
            session['user_id'] = user["id"]
            session['user_name'] = user["name"]
            session['role'] = user["role"]
            return jsonify({
                "success": True,
                "message": "Login successful",
                "name": user["name"],
                "role": user["role"]
            })
        else:
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
    finally:
        cursor.close()
        db.close()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name, email, password, role = data.get("name"), data.get("email"), data.get("password"), data.get("role", "student")

    db = get_db()
    cursor = db.cursor()
    try:
        query = "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, email, password, role))
        return jsonify({"success": True, "message": "User registered successfully"})
    except:
        return jsonify({"success": False, "error": "Email already registered"}), 400
    finally:
        cursor.close()
        db.close()

# ---------------- TASK & ANALYTICS API ---------------- #
@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    db = get_db()
    if not db: return jsonify([]), 500
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    tasks = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(tasks)

# Detailed Stats for Charts
@app.route('/api/analytics/stats', methods=['GET'])
@login_required
def get_stats():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Priority breakdown
    cursor.execute("SELECT priority, COUNT(*) as count FROM tasks GROUP BY priority")
    priority_data = cursor.fetchall()
    
    # Status breakdown
    cursor.execute("SELECT status, COUNT(*) as count FROM tasks GROUP BY status")
    status_data = cursor.fetchall()
    
    db.close()
    return jsonify({
        "priority": priority_data,
        "status": status_data
    })

@app.route('/api/analytics/progress', methods=['GET'])
@login_required
def get_progress():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT status FROM tasks")
    tasks = cursor.fetchall()
    db.close()

    total = len(tasks)
    if total == 0: return jsonify({"percent": 0})
    
    completed = len([t for t in tasks if t['status'] == 'Completed'])
    percent = (completed / total) * 100
    return jsonify({"percent": round(percent, 2), "total": total, "completed": completed})

@app.route('/api/tasks', methods=['POST'])
@login_required
def add_task():
    if session.get('role') != 'admin':
        return jsonify({"success": False, "error": "Unauthorized: Admins only"}), 403
    
    data = request.json
    values = (session['user_id'], data['title'], data.get('description', ''), 'Pending', data['due_date'], data['priority'], datetime.now())
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO tasks (user_id, title, description, status, due_date, priority, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)", values)
    db.close()
    return jsonify({"success": True})

@app.route('/api/tasks/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT status FROM tasks WHERE id=%s", (task_id,))
    task = cursor.fetchone()
    
    if task:
        new_status = 'Completed' if task['status'] == 'Pending' else 'Pending'
        cursor.execute("UPDATE tasks SET status=%s WHERE id=%s", (new_status, task_id))
        db.close()
        return jsonify({"success": True, "new_status": new_status})
    return jsonify({"success": False}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    if session.get('role') != 'admin':
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    db.close()
    return jsonify({"success": True})

# ---------------- AI CHATBOT ROUTE (NAYA API CALL LOGIC) ---------------- #
@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"reply": "Aapne koi message nahi bheja."}), 400

    if not ai_client:
        return jsonify({"reply": "System Error: Backend me AI Client setup nahi hua hai."})

    try:
        system_prompt = f"You are a helpful, professional AI assistant for a project management tool named TaskFlow. Answer concisely and politely. The user says: {user_message}"
        
        # Naye package ka function call
        response = ai_client.models.generate_content(
            model='gemini-2.0-flash',
            contents=system_prompt,
        )
        return jsonify({"reply": response.text})
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return jsonify({"reply": "Maafi chahunga, main abhi theek se connect nahi kar paa raha hu. Thodi der baad try karein."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)