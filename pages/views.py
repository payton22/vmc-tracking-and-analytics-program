import sys

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.http import urlsafe_base64_decode

from login.models import CustomUser
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import update_session_auth_hash, logout, login, tokens

from .forms import CurrentPasswordForm


def landingPageView(request):
    return render(request, 'pages/landingPage.html')

def surveyPageView(request):
    return render(request, 'pages/survey.html')

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

    # When the user submits the form
    if request.method == 'POST':
        # Save the form data
        form = CurrentPasswordForm(request.POST, user=request.user)
        # If the user's current password is correct
        if form.check_entry():
            # Change the password and save it
            request.user.set_password(request.POST.get('pass'))
            # Stay logged in after password is changed
            update_session_auth_hash(request, request.user)
            request.user.save()
            # Change to the page that indicates to the user that
            # the password was successfully changed
            return render(request, 'pages/authPassChangeSuccess.html')
    else:
        # Blank form (no POST yet)
        form = CurrentPasswordForm(user=request.user)

    # Render the current page if the user first enters this page
    # or the user's current password is incorrect
    return render(request, 'pages/changePassPage.html', {'form':form})


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

    info = {'accountName': userAccount.email, 'firstName': userAccount.first_name, 'lastName': userAccount.last_name}
    return render(request, 'pages/individualAccountOption.html', info)


def newAccount(request):
    if request.method == 'POST':
        import hashlib
        import sqlite3

        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(request.POST)

        CustomUser.objects.create_superuser(email, first_name, last_name, password)

        return render(request, 'pages/accountCreated.html', {'email': email})

    return render(request, 'pages/newAccount.html')


def deleteAccount(request, emailAddress):
    user = CustomUser.objects.get(pk=emailAddress)
    print(user.email)
    user.delete()

    return render(request, 'pages/accountDeleted.html', {'email': emailAddress})


def accountCreated(request, emailAddress):
    accountList = accessIndividualAccount(emailAddress)

    email = accountList.email

    return render(request, 'pages/individualAccountOption.html', {'email': email})


def PassReset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            return render(request, 'pages/emailSent.html', {'email': email})

    return render(request, 'pages/forgotPassword.html')


def ChangePass(request, uidb64, token):

    email = urlsafe_base64_decode(uidb64).decode()
    user = CustomUser.objects.get(pk=email)
    tokenChecker = tokens.PasswordResetTokenGenerator()
    if tokenChecker.check_token(user, token):
        login(request, user)
    else:
        raise Http404('Password reset link is no longer valid. Please get another email.')

    return render(request, 'pages/passResetConfirm.html')

# After the user has change their password, log them out and return to the login page
def successfullyChangedPass(request):

    if request.method == 'POST':
        request.user.set_password(request.POST.get('newPassword2'))
        update_session_auth_hash(request, request.user)
        email = request.user.email
        request.user.save()
        logout(request)

    return render(request, 'pages/passChangeSuccess.html', {'email': email})

# Used for sending a test email
# def send_test_mail():
# send_mail('Test subject',
#         'This is the message body',
#        'pjknoch55@gmail.com',
#       ['pjknoch@sbcglobal.net'])
