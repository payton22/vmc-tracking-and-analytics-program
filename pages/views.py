from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect


def landingPageView(request):
    return render(request, 'pages/landingPage.html')


def homePageView(request):
    return render(request, 'pages/homePage.html')


def importPageView(request):
    if request.method == 'POST':
        return HttpResponseRedirect('/parse')
    return render(request, 'pages/importPage.html')


def vmcAdminPageView(request):
    return render(request, "pages/vmcAdminPage.html")


def visPageView(request):
    return render(request, 'pages/visualizationsPage.html')


def changePassView(request):
    return render(request, 'pages/changePassPage.html')


def changeEmailView(request):
    return render(request, 'pages/changeEmailPage.html')


def changeProfileView(request):
    return render(request, 'pages/changeProfilePage.html')


def viewAccountsList(request):
    return render(request, 'pages/viewAccountsList.html')


def accessAccounts():
    import sqlite3;
    # Initialize connection to DB
    conn = sqlite3.connect('vmc_tap.db');
    # Store results of query in table
    email_table = [];
    sql_string = 'SELECT email FROM logins'
    for r in conn.execute(sql_string):
        email_table.append(r);
    # We use this slightly roundabout method instead of something like 'results_table = conn.execute(...)' because conn.execute() does not simply return an array, but rather an open reference the the DB. If left unchecked, you'll lock out the table from being written to for the rest of the session.
    # Close reference to the DB
    conn.close()

    return email_table

def accessIndividualAccount(emailAddress):
    import sqlite3;

    # Initialize connection to DB
    conn = sqlite3.connect('vmc_tap.db');
    # Store results of query in table
    account = [];
    sql_string = 'SELECT * FROM logins WHERE email =\'' + emailAddress + '\';'
    for r in conn.execute(sql_string):
        account.append(r);
    # We use this slightly roundabout method instead of something like 'results_table = conn.execute(...)' because conn.execute() does not simply return an array, but rather an open reference the the DB. If left unchecked, you'll lock out the table from being written to for the rest of the session.
    # Close reference to the DB
    conn.close()

    return account


def flatten(sqlList):
    flattened_list = []
    for listItems in sqlList:
        for item in listItems:
            flattened_list.append(item)

    return flattened_list


def accountsView(request):
    email_list = accessAccounts()
    flattened_email_list = flatten(email_list)

    return render(request, 'pages/viewAccountsList.html', {'emails': flattened_email_list})

def otherAccountOptions(request, emailAddress):
    accountList = accessIndividualAccount(emailAddress)

    accountInfo = flatten(accountList)

    info = {'accountName': accountInfo[0], 'firstName': accountInfo[2], 'lastName':accountInfo[3]}
    return render(request, 'pages/individualAccountOption.html', info)

def newAccount(request):

    if request.method == 'POST':
        import hashlib
        import sqlite3

        conn = sqlite3.connect('vmc_tap.db');

        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(request.POST)

        sql_args = [email, password, firstName, lastName]

        # Encrypt the password
        sql_args[1] = hashlib.md5(sql_args[1].encode('utf-8')).hexdigest();

        # Extracts info from table and insert into database
        conn.execute('INSERT INTO logins VALUES (' + ', '.join(['\'' + str(a) + '\'' for a in sql_args]) + ');')
        # Commit changes to database
        conn.commit()

        return render(request, 'pages/accountCreated.html', {'email' : email})

    return render(request, 'pages/newAccount.html')

def deleteAccount(request, emailAddress):
    import sqlite3
    # Initialize connection to DB
    conn = sqlite3.connect('vmc_tap.db');
    sql_string = 'DELETE FROM logins WHERE email=\'' + emailAddress + '\';'
    # We use this slightly roundabout method instead of something like 'results_table = conn.execute(...)' because conn.execute() does not simply return an array, but rather an open reference the the DB. If left unchecked, you'll lock out the table from being written to for the rest of the session.
    # Close reference to the DB
    conn.execute(sql_string)
    conn.commit()

    return render(request, 'pages/accountDeleted.html', {'email': emailAddress})

def accountCreated(request, emailAddress):
    accountList = accessIndividualAccount(emailAddress)

    accountInfo = flatten(accountList)

    email = accountInfo[0]

    return render(request, 'pages/individualAccountOption.html', {'email' : email})
