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

def newAccount(request):
    return render(request, 'pages/newAccount.html')


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


def accountsView(request):
    email_list = accessAccounts()
    flattened_email_list = []
    for email in email_list:
        for address in email:
            flattened_email_list.append(address)
    return render(request, 'pages/viewAccountsList.html', {'emails': flattened_email_list})
