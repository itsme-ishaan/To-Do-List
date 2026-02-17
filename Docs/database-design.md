# Database Design

## users table
- id (Primary Key)
- name
- email (Unique)
- password
- created_at

## tasks table
- id (Primary Key)
- user_id (Foreign Key)
- title
- description
- status
- due_date
- created_at
