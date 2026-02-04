from django.shortcuts import render
from django.http import HttpResponse
import requests
from .tasks import delay_print
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def index(request):
    if request.method == "POST":
        delay_print.delay()
        print("Button pressed")

    return render(request, "background/index.html")
csrf_exempt

@csrf_exempt
def response(request):
    if request.method == "POST":
        print("DONE")
    return HttpResponse("Callback received")