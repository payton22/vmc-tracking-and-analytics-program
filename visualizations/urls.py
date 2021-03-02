from django.urls import path
from . import views

urlpatterns = [
    path('', views.plotly, name='plotly'),
    path('exampleGraph/', views.exampleGraph, name='exampleGraph'),
    path('getReport/', views.getReport, name='getReport'),
    path('presetReport/<slug:preset_name>/<slug:from_time>/<slug:to_time>/', views.presetReport, name='presetReport'),
    path('getReport/downloadFile/', views.downloadFile, name='downloadFile')
]
