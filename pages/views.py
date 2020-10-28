from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

def landingPageView(request):
    return render(request, 'pages/landingPage.html')

def importPageView(request):
    if request.method == 'POST':
        return HttpResponseRedirect('/parse')
    return render(request, 'pages/importPage.html')
