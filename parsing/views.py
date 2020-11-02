from django.shortcuts import render
from . import scanner_parsing
from django.http import HttpResponse
import csv

import sqlite3

# Create your views here.

def parse(request):
    if request.method == 'POST' and request.FILES['datafile']:
    
        conn = sqlite3.connect('vmc_tap.db');
    
        data_file = request.FILES['datafile'].read().decode('utf-8').splitlines()
        visits = scanner_parsing.parse_scanner_data(data_file)
        return_string = ''
        total_duration = 0
        for visit in visits:
           return_string += str(visit) + '<br>'
           total_duration += visit.duration
           #Insert data into database
           conn.execute(visit.get_insert_statement())
        conn.commit();
        return_string += 'Number of Visits: ' + str(len(visits)) + '.<br>'
        return_string += 'Number of Appointments: ' + str(len(list(filter(lambda x: x.is_appointment,visits)))) + '<br>'
        avg_duration = total_duration/len(list(filter(lambda x: x.duration > 0, visits)))
        return_string += 'Average visit Duration: ' + str(avg_duration)[:5] + 'mins. <br>'
        
        return_string += 'This data has been inserted into the database.<br>'
        
        return HttpResponse(return_string)
    else:
        return HttpResponse("ERROR, please go to the import page and upload a file.")

