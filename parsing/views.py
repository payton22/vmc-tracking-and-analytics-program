from django.shortcuts import render
from . import scanner_parsing
from django.http import HttpResponse
import csv
# Create your views here.

def parse(request):
    if request.method == 'POST' and request.FILES['datafile']:
        data_file = request.FILES['datafile'].read().decode('utf-8').splitlines()
        visits = scanner_parsing.parse_scanner_data(data_file)
        return_string = ''
        total_duration = 0
        for visit in visits:
           return_string += str(visit) + '<br>'
           total_duration += visit.duration
        return_string += 'Number of Visits: ' + str(len(visits)) + '.<br>'
        avg_duration = total_duration/len(visits)
        return_string += 'Average visit Duration: ' + str(avg_duration)[:5] + 'mins. <br>'
        return HttpResponse(return_string)
    else:
        return HttpResponse("ERROR\n")

