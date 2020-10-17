from django.urls import path
from .views import landingPageView

# manages the urls associated with the pages app
urlpatterns = [
    path('', landingPageView, name='landingPage')
]