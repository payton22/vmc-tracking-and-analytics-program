from django.shortcuts import render
from django.http import HttpResponse

def landingPageView(request):
    return render(request, 'pages/landingPage.html')

def homePageView(request):
    return render(request, 'pages/homePage.html')

def importPageView(request):
    return render(request, 'pages/importPage.html')

def vmcAdminPageView(request):
    return render(request, "pages/vmcAdminPage.html")

def visPageView(request):
    return render(request, 'pages/visualizationsPage.html')
