from django.urls import path
from . import views

urlpatterns = [
    path('', views.agent_query, name='agent_query'),
    path('trip/<int:trip_id>/', views.trip_detail, name='trip_detail'),
]