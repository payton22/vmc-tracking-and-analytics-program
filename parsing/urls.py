from django.urls import path
from . import views

urlpatterns = [
        path('', views.parse, name='parse'),
        path('gpa/',views.parse_gpa, name='parse-gpa'),
        path('manual/', views.parse_manual, name='parse-manual'),
]
