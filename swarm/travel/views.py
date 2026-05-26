from django.shortcuts import render, redirect
from .forms import AgentForm
from background.tasks import plan_trip
from .models import Trip
from django.http import JsonResponse, HttpResponse
import markdown2
from markdownify import markdownify as md
import mistune

# View to handle the user trip planning query
def agent_query(request):
    # Handles form submission for trip planning query
    if request.method == 'POST':
        form = AgentForm(request.POST)

        # If the form is valid
        if form.is_valid():

            # Get the cleaned query
            agent_query = form.cleaned_data['agent_query']
            # print("Received agent query:", agent_query)

            # Create trip object in DB with temporary output
            trip = Trip.objects.create(query=agent_query, result="**`PROCESSING`**")
            result = plan_trip.delay(prompt=agent_query, trip_id=trip.id)

            # Redirect user to the page where the trip details will be populated upon completion
            return redirect('trip_detail', trip_id=trip.id)
    else:
        # If not a POST request, render the form for the user to input their trip query
        form = AgentForm()
    
    return render(request, 'travel/agent_query.html', {'form': form})

# View Trip Details
def trip_detail(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    return render(request, 'travel/trip_detail.html', {
        'trip': trip,
        'result_html': mistune.html(trip.result)
    })

# API endpoint to print POST data for debugging
def print_api_post(request):
    if request.method == 'POST':
        data = request.POST
        print("Received API POST data:", data)
        return JsonResponse({'status': 'success', 'data': data})
    else:
        return JsonResponse({'status': 'error', 'data': None})