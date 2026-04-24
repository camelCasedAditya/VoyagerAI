from django.shortcuts import render, redirect
from .forms import AgentForm
from background.tasks import plan_trip
from .models import Trip
from django.http import JsonResponse

# Create your views here.
def agent_query(request):
    if request.method == 'POST':
        form = AgentForm(request.POST)
        if form.is_valid():
            agent_query = form.cleaned_data['agent_query']
            print("Received agent query:", agent_query)
            trip = Trip.objects.create(query=agent_query, result="Processing...")
            result = plan_trip.delay(prompt=agent_query, trip_id=trip.id)
            return redirect('trip_detail', trip_id=trip.id)
    else:
        form = AgentForm()
    
    return render(request, 'travel/agent_query.html', {'form': form})

# View Trip Details
def trip_detail(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    return render(request, 'travel/trip_detail.html', {'trip': trip})

def print_api_post(request):
    if request.method == 'POST':
        data = request.POST
        print("Received API POST data:", data)
        return JsonResponse({'status': 'success', 'data': data})
    else:
        return JsonResponse({'status': 'error', 'data': None})