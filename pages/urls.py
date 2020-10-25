from django.urls import path
from .views import *

# manages the urls associated with the pages app
urlpatterns = [
    path('', landingPageView, name='landingPage'),
    path('home/', homePageView, name="homePage"),
    path('import/', importPageView, name='importPage'),
    path('vmcadmin/', vmcAdminPageView, name='vmcAdminPage')
]