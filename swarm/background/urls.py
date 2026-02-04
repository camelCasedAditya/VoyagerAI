from django.contrib import admin
from django.urls import path
from .views import index, response

urlpatterns = [
    path('test/', index, name='background_index'),
    path("callback/", response, name="response"),
]