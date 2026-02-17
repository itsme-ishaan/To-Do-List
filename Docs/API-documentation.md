# API Documentation

## POST /register
Registers a new user

Body:
{
  "name": "John",
  "email": "john@email.com",
  "password": "123456"
}

---

## POST /login
Authenticates user

---

## GET /tasks/<user_id>
Returns all tasks for a user

---

## POST /tasks
Adds new task

---

## PUT /tasks/<task_id>
Updates task status

---

## DELETE /tasks/<task_id>
Deletes task

