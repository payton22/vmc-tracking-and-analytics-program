from django.shortcuts import render;
import sqlite3;

# Create your views here.
from django.http import HttpResponse;


def index(request):

    return HttpResponse('\'/rebuild_db\' or \'add_superuser\'');
    
def rebuild_db(request):
    conn = sqlite3.connect('vmc_tap.db');
    return_statement = 'Schema rebuilt!<br>';
    
    #Store table list
    tables = [];
    for t in conn.execute('SELECT name FROM sqlite_master WHERE type = \'table\';'):
        for a in t:
            tables.append(str(a));
        
    #Remove tables
    for t in tables:
        conn.execute('DROP TABLE IF EXISTS ' + t + ';');
        
    #Recreate tables
    conn.execute('CREATE TABLE student_barcode(barcode_id TEXT, nhse_id INTEGER)');
    conn.execute('CREATE TABLE visits(time_in TEXT, time_out TEXT, duration REAL, nshe_id TEXT,  event_name TEXT, appointment INTEGER)');
    conn.execute('CREATE TABLE student_demographics(nshe_id INTEGER, rn_net_id TEXT, first_name TEXT, last_name TEXT, acad_career TEXT, units_taken INTEGER, age INTEGER, sex TEXT, ethnicity TEXT, current_gpa REAL, cumulative_gpa REAL, semester_gpa REAL, pell_grant INTEGER, benefit_chapter INTEGER, stem_scholarship INTEGER, residency TEXT, employment TEXT, hrs_per_week TEXT, dependents TEXT, marital_status TEXT, gender TEXT, parent_education TEXT, break_in_attendance INTEGER, needs_based_grants INTEGER, merit_based_grants INTEGER, fed_work_study INTEGER, military_grants INTEGER, millennium_scholarship INTEGER, nv_prepaid INTEGER)');
    conn.execute('CREATE TABLE logins(email TEXT, password TEXT, first_name TEXT, last_name TEXT)');

    
    #Compare table lists
    new_tables = [];
    for t in conn.execute('SELECT name FROM sqlite_master WHERE type = \'table\';'):
        for a in t:
            new_tables.append(str(a));
    
    if(new_tables != tables):
        return_statement = 'Schema not rebuilt correctly!<br>';
    
    return_statement = return_statement + '\n\n\n';
    
    for t in new_tables:
        return_statement = return_statement + t + ':<br>';
        return_statement = return_statement + 'cid, name, type, notnull, defaultval, pk<br>';
        for a in conn.execute('PRAGMA table_info(\'' + t + '\');'):
            return_statement = return_statement + (', '.join([str(b) for b in a])) + '<br>';
        
        return_statement = return_statement + '<br>';
    
    return HttpResponse(return_statement);

def add_superuser(request):
    import hashlib;
    conn = sqlite3.connect('vmc_tap.db');
    
    #Remove tables
    conn.execute('DELETE FROM logins;');
        
    #Recreate tables
    sql_args = ['admin@unr.edu', 'admin', 'Super', 'User']
    sql_args[1] = hashlib.md5(sql_args[1].encode('utf-8')).hexdigest();
    conn.execute('INSERT INTO logins VALUES (' + ', '.join(['\'' + str(a) + '\'' for a in sql_args]) + ');');
    conn.commit();
    
    return HttpResponse(', '.join(sql_args));