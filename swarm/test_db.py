import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swarm.settings')
django.setup()

from travel.models import Trip

def test():
    trip = Trip.objects.get(id=6)
    print("Initial:", trip.result[:20])
    trip.result = "Testing update_fields"
    trip.save(update_fields=['result'])
    
    trip.refresh_from_db()
    print("After:", trip.result[:20])

test()
