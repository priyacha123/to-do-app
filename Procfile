web: gunicorn todoproject.wsgi
release: python manage.py migrate && python manage.py createsuperuser --noinput || true