from django.urls import path
from . import views

urlpatterns = [
        path('', views.index, name='index'),
        path('gpa/',views.gpa, name='gpa'),
]
