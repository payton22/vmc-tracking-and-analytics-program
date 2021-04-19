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
        conn = sqlite3.connect('vmc_tap.db');

        data_file = request.FILES['datafile'].read().decode('utf-8').splitlines()
        formatted_data = gpa_parser.parse_gpa(data_file)
        ret_str = ''
        for student in formatted_data:
            ret_str = ret_str + student.student_name + ' ' + student.cum_gpa + ' ' + student.term + '<br>'
            conn.execute(student.get_insert_statement());
        conn.commit();
        conn.close();
        messages.success(request, "Document Successfully Uploaded." )
        return redirect('importPage')
    else:
        return HttpResponse("ERROR, please go to the import page and upload a file.")


def parse_manual(request):
    if request.method == 'POST':
        import re;
        import datetime;
        conn = sqlite3.connect('vmc_tap.db');
        input_dict = {}
        
        #Create a dictionary out of the list of items. Might already be a dictionary; rather be safe here.
        max_record = 0;
        for a in request.POST.items():
            if(a[0] == 'csrfmiddlewaretoken'):
                continue;
            input_dict[a[0]] = a[1]
            if(int(a[0][-1:]) > max_record):
                max_record = int(a[0][-1:]);
        
        
        #This is a list of what can be entered by the user.
        fields_list = ['NSHEID', 'fname', 'lname', 'location', 'checkintime', 'checkouttime']

        #This is a list of SQL variables.
        sql_list = ['student_id', 'student_name', 'location', 'check_in_date', 'check_in_time', 'check_out_date', 'check_out_time', 'check_in_duration']

        #For each record entered...
        for i in range(0,max_record + 1):

            #Is the student already in our DB?
            #We use the NSHE ID to figure it out. They might not have entered an NSHE ID, so for now, leave it as None.
            student_exists = None;

            #Prep an array to use as a basis for forming the final SQL statement.
            this_record = ["\'\'"] * 8;

            #Now try to find fields that are filled out.
            for index, f in enumerate(fields_list):
                
                #If we find a field that is filled out, store the input into a variable for easy access.
                if(input_dict.get(f + str(i))):
                    this_input = input_dict.get(f + str(i));

                    #If they entered an NSHEID, we can query the DB to see if the student already exists.
                    if(f == 'NSHEID'):
                        for d in conn.execute('SELECT count(*), student_name FROM demographics WHERE student_id = ' + str(this_input) + ';'):
                            student_exists = d[0];

                            #No matter what, we include the NSHEID as a part of the query.
                            this_record[0] = "'" + str(this_input) + "'";

                            #If the student exists, we want to use their existing name, and not update it...
                            #Unless that name is incomplete. Names with one word are not complete.
                            #Since we only use the existing name if they enter an NSHEID, the rest of the name code
                            #Will be dealt with later.
                            if(d[0] > 0 and d[1].find(' ') != -1):
                                this_record[1] = "'" + d[1] + "'";

                    elif((f == 'fname' or f == 'lname') and this_record[1] == "\'\'"):
                        #At this point, if the name is still blank, we need to assemble a new one.
                        #If both first and name are included, use that.
                        if(input_dict.get('fname' + str(i)) and input_dict.get('lname' + str(i))):
                            this_record[1] = "'" + input_dict.get('fname' + str(i)) + ' ' + input_dict.get('lname' + str(i)) + "'";

                        #If only one name is included, use that. If no name is provided, oh well, leave it blank.
                        elif(input_dict.get('fname' + str(i)) and not input_dict.get('lname' + str(i))):
                            this_record[1] = "'" + input_dict.get('fname' + str(i)) + "'";
                        elif(not input_dict.get('fname' + str(i)) and input_dict.get('lname' + str(i))):
                            this_record[1] = "'" + input_dict.get('fname' + str(i)) + "'";

                    elif(f == 'location'):
                        this_record[2] = "'Veteran Services " + this_input + "'";

                    elif(f == 'checkintime'):
                        #Ensure the format is correct; if so, split it into a date and time.
                        m = re.fullmatch('\d{2}\/\d{2}\/\d{4}T\d{2}:\d{2}',this_input);
                        if(m):
                            this_date = this_input[0:this_input.index('T')]
                            this_time = this_input[this_input.index('T')+1:]
                            this_record[3] = "'" + datetime.datetime.strptime(this_date, "%m/%d/%Y").strftime("%Y-%m-%d") + "'"
                            this_record[4] = "'" + datetime.datetime.strptime(this_time, "%H:%M").strftime("%I:%M %p") + "'"
                    elif(f == 'checkouttime'):
                        m = re.fullmatch('\d{2}\/\d{2}\/\d{4}T\d{2}:\d{2}',this_input);
                        if(m):
                            this_date = this_input[0:this_input.index('T')]
                            this_time = this_input[this_input.index('T')+1:]
                            this_record[5] = "'" + datetime.datetime.strptime(this_date, "%m/%d/%Y").strftime("%Y-%m-%d") + "'"
                            this_record[6] = "'" + datetime.datetime.strptime(this_time, "%H:%M").strftime("%I:%M %p") + "'"

                    #this_record[index] = f;
                else:
                    continue;

            #Check if the check in and out dates are both filled out; if so, we can construct a check in duration
            if(this_record[3] != "\'\'" and this_record[5] != "\'\'"):
                #Construct datetime objects to do a time difference
                chk_in = datetime.datetime.strptime(this_record[3].replace("'","") + ' ' + this_record[4].replace("'",""), "%Y-%m-%d %I:%M %p")
                chk_out = datetime.datetime.strptime(this_record[5].replace("'","") + ' ' + this_record[6].replace("'",""), "%Y-%m-%d %I:%M %p")

            elif(this_record[3] == "\'\'" and this_record[5] != "\'\'"):
                #We assume the check-in date is the same as the check out date
                chk_in = datetime.datetime.strptime(this_record[5].replace("'","") + ' ' + this_record[6].replace("'",""), "%Y-%m-%d %I:%M %p")
                chk_out = datetime.datetime.strptime(this_record[5].replace("'","") + ' ' + this_record[6].replace("'",""), "%Y-%m-%d %I:%M %p")

                this_record[3] = "'" + chk_out.strftime("%Y-%m-%d") + "'"
                this_record[4] = "'" + chk_out.strftime("%I:%M %p") + "'"

            elif(this_record[3] != "\'\'" and this_record[5] == "\'\'"):
                #We assume the check-out date is the same as the check in date
                chk_in = datetime.datetime.strptime(this_record[3].replace("'","") + ' ' + this_record[4].replace("'",""), "%Y-%m-%d %I:%M %p")
                chk_out = datetime.datetime.strptime(this_record[3].replace("'","") + ' ' + this_record[4].replace("'",""), "%Y-%m-%d %I:%M %p")

                this_record[5] = "'" + chk_in.strftime("%Y-%m-%d") + "'"
                this_record[6] = "'" + chk_in.strftime("%I:%M %p") + "'"

            else:
                #We set the check in and check out times to the current time
                chk_in = datetime.datetime.now()
                chk_out = datetime.datetime.now()

                this_record[3] = "'" + chk_out.strftime("%Y-%m-%d") + "'"
                this_record[4] = "'" + chk_out.strftime("%I:%M %p") + "'"
                this_record[5] = "'" + chk_in.strftime("%Y-%m-%d") + "'"
                this_record[6] = "'" + chk_in.strftime("%I:%M %p") + "'"

            this_record[7] = "'" + str(max(round((chk_out - chk_in).total_seconds() / 60.0,2),0.0)) + "'"
            #Record built, add to DB
            sql_statement = 'INSERT INTO visits (';
            sql_statement += ', '.join(sql_list);
            sql_statement += ') VALUES (';
            sql_statement += ', '.join(this_record);
            sql_statement += ');';
            conn.execute(sql_statement);

        conn.commit();
        conn.close();
    #return HttpResponse(input_dict);
    messages.success(request, "Manual Data Successfully Uploaded." )
    return redirect('importPage')

