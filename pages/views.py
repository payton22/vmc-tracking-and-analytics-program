from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

def landingPageView(request):
    return render(request, 'pages/landingPage.html')

def homePageView(request):
    return render(request, 'pages/homePage.html')

def importPageView(request):
    if request.method == 'POST':
        return HttpResponseRedirect('/parse')
    return render(request, 'pages/importPage.html')

def vmcAdminPageView(request):
    return render(request, "pages/vmcAdminPage.html")

def visPageView(request):
    return render(request, 'pages/visualizationsPage.html')

def changePassView(request):
    return render(request, 'pages/changePassPage.html')

def changeEmailView(request):
    return render(request, 'pages/changeEmailPage.html')

def changeProfileView(request):
    return render(request, 'pages/changeProfilePage.html')
