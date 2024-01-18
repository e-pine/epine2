from django.urls import path
from .import views
# app_name = 'stats'
urlpatterns = [
    path('dashboard/<slug>/', views.dashboard, name='dashboard'),
    path('main/', views.main, name='main'),
    path('dashboard/<slug>/chart/', views.chart_data, name='chart_data'),
]
