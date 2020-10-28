from django.urls import path
from .views import *

# manages the urls associated with the pages app
urlpatterns = [
    path('', landingPageView, name='landingPage'),
    path('import/', importPageView, name='importPage')
]