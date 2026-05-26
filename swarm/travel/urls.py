from django.urls import path
from . import views

# Routing for webapp
urlpatterns = [
    path('', views.agent_query, name='agent_query'),

    # Route to view trip plan
    path('trip/<int:trip_id>/', views.trip_detail, name='trip_detail'),
    
    path('api/print_post/', views.print_api_post, name='print_api_post'),
]