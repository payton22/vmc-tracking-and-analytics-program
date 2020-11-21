from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from login.models import CustomUser

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
    users = CustomUser.objects.all()

    return users

def accessIndividualAccount(emailAddress):
    user = CustomUser.objects.get(pk=emailAddress)

    return user


def flatten(sqlList):
    flattened_list = []
    for listItems in sqlList:
        for item in listItems:
            flattened_list.append(item)

    return flattened_list


def accountsView(request):
    accountsList = accessAccounts()
    emails = []

    for user in accountsList:
        emails.append(user.email)

    return render(request, 'pages/viewAccountsList.html', {'emails': emails})

def otherAccountOptions(request, emailAddress):
    userAccount = accessIndividualAccount(emailAddress)


    info = {'accountName': userAccount.email, 'firstName': userAccount.first_name, 'lastName':userAccount.last_name}
    return render(request, 'pages/individualAccountOption.html', info)

def newAccount(request):

    if request.method == 'POST':
        import hashlib
        import sqlite3

        conn = sqlite3.connect('vmc_tap.db');

        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(request.POST)

        CustomUser.objects.create_user(email, first_name, last_name, password)

        return render(request, 'pages/accountCreated.html', {'email' : email})

    return render(request, 'pages/newAccount.html')

def deleteAccount(request, emailAddress):
    user = CustomUser.objects.get(pk=emailAddress)
    print(user.email)
    user.delete()

    return render(request, 'pages/accountDeleted.html', {'email': emailAddress})

def accountCreated(request, emailAddress):
    accountList = accessIndividualAccount(emailAddress)

    email = accountList.email

    return render(request, 'pages/individualAccountOption.html', {'email' : email})
