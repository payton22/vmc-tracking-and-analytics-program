from django.shortcuts import render;
import sqlite3;

# Create your views here.
from django.http import HttpResponse;


def index(request):

    conn = sqlite3.connect('vmc_tap.db');
    string = '';
    # Execute the query
    conn.execute('DROP TABLE IF EXISTS test;');
    conn.execute('CREATE TABLE test (col1 INTEGER);');
    conn.execute('INSERT INTO test VALUES (1);');
    conn.execute('INSERT INTO test VALUES (2);');
    conn.execute('INSERT INTO test VALUES (6);');
    conn.commit();
    for r in conn.execute('SELECT * FROM test;'):
        string = string + ', '.join([str(a) for a in r]) + '\n';
    conn.execute('DROP TABLE test;');
    conn.close();

    return HttpResponse(string);
    
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
    conn.execute('CREATE TABLE student(barcodeID TEXT, nhseID INTEGER, netID TEXT, full_name TEXT, gender INTEGER)');
    conn.execute('CREATE TABLE visits(time_in TEXT, time_out TEXT, duration REAL, barcodeID TEXT, event_id INTEGER, event_name TEXT, appointment INTEGER)');
    conn.execute('CREATE TABLE questionnaire(netID INTEGER, nhseID TEXT, timestamp TEXT, benefit_chapter INTEGER, stem_scholarship INTEGER, currently_living BLOB, employment BLOB, num_hrs_working BLOB, pell_grant INTEGER, needs_based_grants INTEGER, merit_based_grants INTEGER, federal_work_study INTEGER, military_grants INTEGER, millennium_scholarship INTEGER, nevada_pre_paid INTEGER, num_dependents BLOB, marital_status BLOB, gender INTEGER, sexual_orientation BLOB, parent_education BLOB, break_in_attendance INTEGER)');
    conn.execute('CREATE TABLE logins_md5(username TEXT, password TEXT, email TEXT, first_name TEXT, last_name TEXT)');
    
    #for i in range(0, 75):
    #    conn.execute('INSERT INTO logins_md5 VALUES(\'a\', \'b\', \'c\', \'d\', \'e\');');
    #conn.commit();
    
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