USE student_task_db;

-- Users insert
INSERT INTO users (id, username, password) VALUES 
(1, 'admin', 'admin123'),
(2, 'ishaan', 'password');

-- Tasks insert
INSERT INTO tasks (id, user_id, title, status) VALUES 
(1, 1, 'Setup project', 'pending'),
(2, 2, 'Create login page', 'pending'),
(3, 1, 'Connect backend with MySQL', 'pending');
