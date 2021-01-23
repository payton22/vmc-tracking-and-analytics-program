from django.urls import path
from . import views

urlpatterns = [
    path('', views.plotly, name='plotly'),
    path('exampleGraph/', views.exampleGraph, name='exampleGraph'),
    path('getReport/', views.getReport, name='getReport'),
]
