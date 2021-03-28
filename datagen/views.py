from django.shortcuts import render
from django.http import HttpResponse
from .forms import DateForm
from .datagen import gen_report
from .gpa import gen_gpa_data

import os
# Create your views here.

def index(request):
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            gen_report('report.csv',form.cleaned_data['date'])
            content = open('report.csv').read()
            response = HttpResponse(content)
            response['Content-Type'] = 'text/plain'
            response['Content-Disposition'] = 'attachment; filename=report.csv'
            os.remove('report.csv')
            return response
    else:
        form = DateForm()

    return render(request,'datagen/index.html', {'form': form})

def gpa(request):
    gen_gpa_data('gpa.csv')
    content = open('gpa.csv').read()
    response = HttpResponse(content)
    response['Content-Type'] = 'text/plain'
    response['Content-Disposition'] = 'attachment; filename=gpa.csv'
    os.remove('gpa.csv')
    return response
