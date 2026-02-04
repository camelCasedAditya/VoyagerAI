from django.conf import settings
from django.core.mail import send_mail
from swarm import celery_app
import time
import requests

@celery_app.task()
def delay_print():
    print("START")
    time.sleep(10)
    url = 'http://127.0.0.1:8000/background/callback/'
    myobj = {'somekey': 'somevalue'}

    headers = {'X-CSRFToken': 'bypass'}
    x = requests.post(url, json=myobj, timeout=10, headers=headers)
    
    print("This is a delayed print task.")