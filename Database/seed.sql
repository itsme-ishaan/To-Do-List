USE student_task_db;

-- Purana data saaf karna taaki naya fresh data insert ho sake
DELETE FROM tasks;
DELETE FROM users;

-- Naye Users Insert karein (Admin aur Student)
INSERT INTO users (id, name, email, password, role) VALUES 
(1, 'Ishaan Gaur', 'ishaan@admin.com', 'admin123', 'admin'),
(2, 'Test Student', 'ishaan@user.com', 'user123', 'student');

-- Presentation ke liye Realistic Tasks Insert karein (Aapke subjects ke hisaab se)
INSERT INTO tasks (id, user_id, title, description, status, priority, due_date) VALUES 
(1, 1, 'Setup TaskFlow Database', 'Execute schema.sql and seed.sql to initialize system.', 'Completed', 'High', '2026-02-24'),
(2, 2, 'Advanced Java Assignment', 'Complete Spring Boot API endpoints for the backend.', 'Pending', 'High', '2026-02-28'),
(3, 1, 'Cloud Computing Lab', 'Deploy Docker containers on AWS EC2 instance.', 'Pending', 'Medium', '2026-03-02'),
(4, 2, 'Generative AI Minor Project', 'Integrate RAG pipeline with LLM API for the chatbot.', 'Pending', 'High', '2026-03-10'),
(5, 1, 'Competitive Coding Practice', 'Solve 5 DP and Graph problems on LeetCode.', 'Pending', 'Low', '2026-03-05'),
(6, 2, 'Agile SE Presentation', 'Prepare slides for Scrum methodology and sprint planning.', 'Completed', 'Medium', '2026-02-20');