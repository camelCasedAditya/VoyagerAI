import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swarm.settings')
django.setup()
from travel.models import Trip
from background.tasks import plan_trip

trip = Trip.objects.get(id=8)
try:
    print("Testing update:", trip.id)
    Trip.objects.filter(id=8).update(result="Success!")
    trip.refresh_from_db()
    print("Result:", trip.result)
except Exception as e:
    print("Error:", e)
