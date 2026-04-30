How to run (All in different terminals in "./swarm"):

Redis
redis-server

Django
python manage.py runserver

Celery worker
../env/bin/celery -A swarm worker -l info