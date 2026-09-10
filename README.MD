# Django To-Do App

A multi-user to-do list built with Django. Features user auth, categories, due dates with overdue highlighting, search, and pagination.

## Live Demo
https://your-app.onrender.com

## Tech
Django, PostgreSQL, Bootstrap 5, deployed on Render

## Features
- User signup/login, per-user task isolation
- CRUD for tasks
- Categories/tags
- Due dates with overdue highlighting
- Search + pagination

## Local Setup
1. `python -m venv .venv && .venv/Scripts/activate`
2. `pip install -r requirements.txt`
3. Create a `.env` file with `SECRET_KEY`, `DEBUG=True`
4. `python manage.py migrate`
5. `python manage.py runserver`