from django.shortcuts import render, redirect
from django.contrib import messages
from . import scanner_parsing
from . import parser
from . import gpa_parser
from django.http import HttpResponse
import csv

import sqlite3


# Create your views here.

def parse(request):
    if request.method == 'POST' and request.FILES['datafile']:

        conn = sqlite3.connect('vmc_tap.db');

        data_file = request.FILES['datafile'].read().decode('utf-8').splitlines();
        data, tags = parser.parse_report(data_file);
        return_string = '';
        total_duration = 0;

        query_names = ['student_name', 'student_email', 'student_id', 'classification', 'major'];
        #First compile a list of new students
        new_students = [];

        #To do this, we need the list of all existing students (this may get slower as the years pass)
        existing_students = [];
        get_students = "SELECT DISTINCT student_id FROM demographics;";
        for d in conn.execute(get_students):
                    existing_students.append(d);

        for visit in data:
            #return_string += str(visit) + '<br>';
            #Check if student exists; if not, add to new_students.
            if(visit.student_id not in [student_id for student_id, _ in new_students] and visit.student_id not in existing_students):
                new_students.append((visit.student_id, visit));

        #conn.execute("BEGIN TRANSACTION;");
        #Add all new students to demographics table
        for _, this_student_visit in new_students:
            query_values = [this_student_visit.student_name, this_student_visit.student_email, this_student_visit.student_id, this_student_visit.classification, this_student_visit.major];
            query_values = ['\'' + str(a) + '\'' for a in query_values]

            demographics_query = 'INSERT INTO demographics (' + ', '.join(query_names) + ') VALUES (' + ', '.join(query_values) + ');';
            conn.execute(demographics_query);
        #conn.execute("COMMIT;");
        conn.commit();


        #Now add all visits data
        #conn.execute("BEGIN TRANSACTION;");
        query_names = ['student_name', 'student_email', 'classification', 'major'];
        query_commas = [', ',', ',', ',' '];
        for visit in data:
            # Insert visit data into database
            conn.execute(visit.get_insert_statement())

            #Get demographics data
            query_values = [visit.student_name, visit.student_email, visit.classification, visit.major];
            query_values = ['\'' + str(a) + '\'' for a in query_values]
            
            #Update record
            demographics_query = 'UPDATE demographics SET ';
            for i, name in enumerate(query_names):
                demographics_query += name + ' = ' + query_values[i] + query_commas[i];
            demographics_query += 'WHERE student_id = ' + str(visit.student_id) + ';';
            conn.execute(demographics_query);
                
        #conn.execute("COMMIT;");
        conn.commit();
        return_string += 'Number of Visits: ' + str(len(data)) + '.<br>'

        # return_string += 'This data has been inserted into the database.<br>'
        conn.close();
        messages.success(request, "Document Successfully Uploaded." )
        return redirect('importPage')
    else:
        return HttpResponse("ERROR, please go to the import page and upload a file.")

def parse_gpa(request):
    if request.method == 'POST' and request.FILES['datafile']:
        data_file = request.FILES['datafile'].read().decode('utf-8').splitlines()
        formatted_data = gpa_parser.parse_gpa(data_file)
        ret_str = ''
        for student in formatted_data:
            ret_str = ret_str + student.student_name + ' ' + student.cum_gpa + '<br>'
        return HttpResponse(ret_str)
    else:
        return HttpResponse("ERROR, please go to the import page and upload a file.")

