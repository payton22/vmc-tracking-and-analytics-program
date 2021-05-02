from django.urls import path
from . import views

# Provides the url paths for each page and view in the visualizations (now known as 'Reports') app
urlpatterns = [
    path('', views.plotly, name='plotly'),
    path('exampleGraph/', views.exampleGraph, name='exampleGraph'),
    path('getReport/', views.getReport, name='getReport'),
    path('presetReport/<path:preset_name>/<slug:from_time>/<slug:to_time>/', views.presetReport, name='presetReport'),
    path('getReport/downloadFile/', views.downloadFile, name='downloadFile')
]
