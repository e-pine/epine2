release: python manage.py migrate
web: daphne epine.asgi:application --port $PORT --bind 0.0.0.0 -v2
celery: celery -A epine.celery worker --pool=solo -l info
celerybeat: celery -A epine beat -l INFO