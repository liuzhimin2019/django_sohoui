from django.contrib import admin
from django.urls import path, include
from django_sohoui import views 

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard1/', views.dashboard1, name='dashboard1'),
    path('get_data/', views.get_data, name='get_data'),
    path('upload/', views.upload, name='upload'),
    path('delete_selected_confirmation/', views.delete_selected_confirmation, name='delete_selected_confirmation'), 
    path('custom_url/', views.custom_url, name='custom_url'),
    path('home/', views.home, name='home'),
    path('test/', views.test, name='test')
]