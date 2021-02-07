from django.shortcuts import render;
import sqlite3;

# Create your views here.
from django.http import HttpResponse;


def index(request):
    return HttpResponse('\'/rebuild_db\' or \'add_superuser\'');


def rebuild_db(request):
    conn = sqlite3.connect('vmc_tap.db');
    return_statement = 'Schema rebuilt!<br>';

    # Store table list
    remove_tables = ['student_barcode'];

    tables = ['visits', 'demographics', 'tags', 'logins', 'cat_hours'];

    # Remove tables
    for t in remove_tables:
        conn.execute('DROP TABLE IF EXISTS ' + t + ';');
    for t in tables:
        conn.execute('DROP TABLE IF EXISTS ' + t + ';');

    # Recreate tables
    conn.execute(
        'CREATE TABLE visits(student_name TEXT, student_email TEXT, student_id INTEGER, student_alt_id TEXT, classification TEXT, major TEXT, assigned_staff TEXT, care_unit TEXT, services TEXT, course_name TEXT, course_number TEXT, location TEXT, check_in_date DATE, check_in_time TEXT, check_out_date DATE, check_out_time TEXT, check_in_duration REAL, staff_name TEXT,staff_id TEXT, staff_email TEXT)');
    conn.execute(
        'CREATE TABLE demographics(student_name TEXT, student_email TEXT, student_id INTEGER, student_alt_id TEXT, classification TEXT, cumulative_gpa REAL, assigned_staff TEXT, cell_phone TEXT, home_phone TEXT, gender TEXT, ethnicity TEXT, date_of_birth TEXT, address TEXT, additional_address TEXT, city TEXT, state TEXT, zip TEXT, term_credit_hours REAL, term_gpa REAL, total_credit_hours_earned REAL, sms_opt_out INTEGER, datetime_opt_out TEXT, can_be_sent_messages INTEGER)');

    conn.execute('CREATE TABLE cat_hours(hour_display TEXT, ordering INTEGER)');
    conn.execute("INSERT INTO cat_hours VALUES ('12 AM', 0)");
    for i in range(1,12):
        conn.execute("INSERT INTO cat_hours VALUES ('" + str(i) +" AM', " + str(i) + ")");
    conn.execute("INSERT INTO cat_hours VALUES ('12 PM', 12)");
    for i in range(1,12):
        conn.execute("INSERT INTO cat_hours VALUES ('" + str(i) +" PM', " + str(i+12) + ")");


    conn.execute('CREATE TABLE tags(student_id INTEGER, tag TEXT, date TEXT)');
    conn.commit();

    return_statement = return_statement + '\n\n\n';

    for t in tables:
        return_statement = return_statement + t + ':<br>';
        return_statement = return_statement + 'cid, name, type, notnull, defaultval, pk<br>';
        for a in conn.execute('PRAGMA table_info(\'' + t + '\');'):
            return_statement = return_statement + (', '.join([str(b) for b in a])) + '<br>';

        return_statement = return_statement + '<br>';

    return HttpResponse(return_statement);
