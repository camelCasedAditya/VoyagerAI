# Sets up Celery to run async background tasks and is configured to use Redis as a queue for tasks pending.
# Allows Django app to run while long tasks are complete in the background

import os
from celery import Celery

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 
    'swarm.settings'
)

app = Celery('swarm', broker='redis://127.0.0.1:6379/0')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()