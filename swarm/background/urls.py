from django.contrib import admin
from django.urls import path
from .views import index

urlpatterns = [
    path('test/', index, name='background_index'),
]