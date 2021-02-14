from django.shortcuts import render
from . import scanner_parsing
from . import parser
from django.http import HttpResponse
import csv

import sqlite3


# Create your views here.

def parse(request):
    if request.method == 'POST' and request.FILES['datafile']:

        conn = sqlite3.connect('vmc_tap.db');

        data_file = request.FILES['datafile'].read().decode('utf-8').splitlines()
        data, tags = parser.parse_report(data_file)
        return_string = ''
        total_duration = 0
        for visit in data:
            return_string += str(visit) + '<br>'
            # Insert visit data into database
            conn.execute(visit.get_insert_statement())

            #Check if student exists; if not, insert new demographic record. If so, update it.
            conn_results = '';
            does_student_exist = 'SELECT count(*) FROM demographics WHERE student_id = ' + str(visit.student_id) + ';';
            for d in conn.execute(does_student_exist):
                conn_results.append(d);

            query_names = ['student_name', 'student_email', 'classification', 'major']
            query_values = [visit.student_name, visit.student_email, visit.classification, visit.major];
            query_values = ['\'' + str(a) + '\'' for a in query_values]
            query_commas = [', ',', ',', ',' ']

            #Check if the student exists in the demographics table
            if(conn_results[0] == [1]):
                demographics_query = 'UPDATE demographics SET ';
                for i, name in enumerate(query_names):
                    demographics_query += name + ' = ' + query_values[i] + query_commas[i];
                demographics_query += 'WHERE student_id = ' + str(visit.student_id) + ';';
                conn.execute(demographics_query);
                #We do not have to commit here, since this is an update statement. This saves on processing time.
            else:
                return_string += ','.join(conn_results[0]) + '<br>'
                demographics_query = 'INSERT INTO demographics (' + ', '.join(query_names) + ') VALUES (' + ', '.join(query_values) + ');';
                conn.execute(demographics_query);
                #We must commit here, otherwise if a student is not in demographics yet exists in this dataset multiple times, they will have duplicate entries in the demographics table.
                conn.commit();

                
        conn.commit();
        return_string += 'Number of Visits: ' + str(len(data)) + '.<br>'

        # return_string += 'This data has been inserted into the database.<br>'

        return HttpResponse(return_string)
    else:
        return HttpResponse("ERROR, please go to the import page and upload a file.")
