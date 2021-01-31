from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('rebuild_database', views.rebuild_db, name='rebuild_db'),
    #path('add_superuser', views.add_superuser, name='add_superuser'),
]