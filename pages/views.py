import sys

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.http import urlsafe_base64_decode

from login.models import CustomUser
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import update_session_auth_hash, logout, login, tokens
from formtools.wizard.views import SessionWizardView
from .forms import *

FORMS = [('SelectReportType', SelectReportType),
         ('BarGraphAxes', BarGraphAxes),
         ('LineGraphAxes', BarGraphAxes),
         ('HistogramAxes', HistogramAxes),
         ('PieChartData', BarGraphAxes),
         ('ScatterPlotAxes', BarGraphAxes),
         ('IndividualStatisticOptions', IndividualStatisticOptions),
         ('TimeFrame', TimeFrame),
         ('CustomizeBarGraph', CustomizeBarGraph),
         ('CustomizeLineGraph', CustomizeLineGraph),
         ('CustomizeScatterPlot', CustomizeScatterPlot),
         ('PieChartDetails', PieChartDetails),
         ('HistogramDetails', HistogramDetails),
         ('IndividualStatisticDetails', IndividualStatisticDetails),
         ('AttendanceDataForm', AttendanceDataForm),
         ('ConfirmBarGraph', forms.Form), # Just use the default Django form class for these,
         ('ConfirmHistogram', forms.Form), # since we are not asking for any input
         ('ConfirmLineGraph', forms.Form)]

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


def changePassView(request, emailAddress):
    # Get the info. from the selected account
    user = accessIndividualAccount(emailAddress)
    email = user.email
    # When the user submits the form
    if request.method == 'POST':
        # Save the form data
        form = CurrentPasswordForm(request.POST, user=request.user)
        # If the user's current password is correct
        if form.check_entry():

            # If the user is changing their own password
            if user.email == request.user.email:
                # Set password with new value, save
                request.user.set_password(request.POST.get('pass'))
                request.user.save()
                # Stay authenticated
                update_session_auth_hash(request, request.user)
            else:
                # Set password with new value, save
                user.set_password(request.POST.get('pass'))
                user.save()

            # Change to the page that indicates to the user that
            # the password was successfully changed
            return render(request, 'pages/authPassChangeSuccess.html', {'email': email})
    else:
        # Blank form (no POST yet)

        form = CurrentPasswordForm(user=request.user)

    # Render the current page if the user first enters this page
    # or the user's current password is incorrect
    return render(request, 'pages/changePassPage.html', {'form': form, 'email': email})


def changeEmailView(request, email):
    # Get the info. from the selected account
    user = accessIndividualAccount(email)
    previous_email = email
    email = user.email
    # When the user submits the form
    if request.method == 'POST':
        # Save the form data
        form = ChangeEmailForm(request.POST, user=request.user)
        # If the user's current password is correct
        # TODO check if all attributes are saved when a copy is created
        if form.check_entry():
            if request.user.email == user.email:
                saved_user = request.user
                logout(request)
                user.email = request.POST.get('email_confirm')
                user.save()
                saved_user.delete()
                login(request, user)
            else:

                old_user_email = user.email
                user.email = request.POST.get('email_confirm')
                user.save()

                old_user_acct = CustomUser.objects.get(pk=old_user_email)
                old_user_acct.delete()

            # Change to the page that indicates to the user that
            # the password was successfully changed
            return render(request, 'pages/emailChangeSuccess.html', {'email': user.email})
    else:
        # Blank form (no POST yet)

        form = ChangeEmailForm(user=request.user)

    # Render the current page if the user first enters this page
    # or the user's current password is incorrect
    return render(request, 'pages/changeEmailPage.html', {'form': form, 'email': email})


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


def changeName(request, accountName):
    # Get the info. from the selected account
    user = accessIndividualAccount(accountName)
    email = user.email
    # When the user submits the form
    if request.method == 'POST':
        # Save the form data
        form = ChangeNameForm(request.POST, user=request.user)
        # If the user's current password is correct
        if form.check_entry():
            # Change the user's first and last name
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.save()

            return render(request, 'pages/nameChangeSuccess.html', {'email': email})
    else:
        # Blank form (no POST yet)

        form = ChangeNameForm(user=request.user)

    # Render the current page if the user first enters this page
    # or the user's current password is incorrect
    return render(request, 'pages/changeName.html', {'form': form, 'email': email})


def profileImageView(request, accountName):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, user=request.user)
        user = accessIndividualAccount(accountName)
        if form.check_entry():
            user.avatar = request.FILES.get('prof_pic')
            user.save()
        return render(request, 'pages/successfullyChangedProfPic.html', {'email': user.email})
    else:
        form = UserProfileForm()
        return render(request, 'pages/changeProfilePic.html', {'form': form, 'email': accountName})


# Check if the user selects 'Bar Graph'
def barGraphWizard(wizard):
    return conditionalWizardBranch(wizard, 'Bar Graph')


# Check if the user selects 'Histogram'
def histogramWizard(wizard):
    return conditionalWizardBranch(wizard, 'Histogram')

# Branch to line graph wizard if user selects 'Line Graph'
def lineGraphWizard(wizard):
    return conditionalWizardBranch(wizard, 'Line Graph')

# Branch to pie chart wizard if user selects 'Pie Chart' on first page
def pieChartWizard(wizard):
    return conditionalWizardBranch(wizard, 'Pie Chart')

# Branch to scatter plot wizard if user selects 'Scatter Plot' on first page
def scatterPlotWizard(wizard):
    return conditionalWizardBranch(wizard, 'Scatter Plot')

# Branch to individual statistic wizard if user selects 'Individual Statistic'
# on first page
def individualStatisticWizard(wizard):
    return conditionalWizardBranch(wizard, 'Individual Statistic')


# On the first page of the Reports Wizard, the user will select a graph type
# (e.g. Bar Graph, Histogram, Pie Chart...). The expected selection for a given graph
# type is passed as an argument, which is then compared to the user's choice.
def conditionalWizardBranch(wizard, graphType):
    # Get the user's choice (e.g. Bar Graph, Histogram, Pie Chart, etc.)
    cleaned_data = wizard.get_cleaned_data_for_step('SelectReportType') or {}
    # If the user's selection matches the graph type, return True
    if cleaned_data.get('graphType') == graphType:
        return True
    else:
        return False


class ReportWizardBase(SessionWizardView):
    choices_dict = {}
    TEMPLATES = {'SelectReportType': 'pages/selectGraph.html',
                 'BarGraphAxes': 'pages/WizardFiles/barGraphAxes.html',
                 'LineGraphAxes': 'pages/WizardFiles/barGraphAxes.html',
                 'HistogramAxes': 'pages/WizardFiles/histogramFreq.html',
                 'ScatterPlotAxes': 'pages/WizardFiles/barGraphAxes.html',
                 'PieChartData' : 'pages/WizardFiles/barGraphAxes.html',
                 'IndividualStatisticOptions': 'pages/WizardFiles/individualStatisticOptions.html',
                 'TimeFrame': 'pages/WizardFiles/timeFrame.html',
                 'CustomizeBarGraph': 'pages/WizardFiles/customizeBarGraph.html',
                 'CustomizeLineGraph': 'pages/WizardFiles/customizeLineGraph.html',
                 'CustomizeScatterPlot': 'pages/WizardFiles/customizeBarGraph.html',
                 'AttendanceDataForm': 'pages/WizardFiles/attendanceLocation.html',
                 'ConfirmBarGraph': 'pages/WizardFiles/confirmationBarGraph.html',
                 'HistogramDetails': 'pages/WizardFiles/histogramDetails.html',
                 'PieChartDetails': 'pages/WizardFiles/histogramDetails.html',
                 'IndividualStatisticDetails': 'pages/WizardFiles/histogramDetails.html',
                 'ConfirmHistogram':'pages/WizardFiles/confirmHistogram.html',
                 'ConfirmLineGraph': 'pages/WizardFiles/confirmLineGraph.html', }
                # 'selection': choices_dict} commented out for now

    def get_context_data(self, form, **kwargs):
        context = super(ReportWizardBase, self).get_context_data(form=form, **kwargs)
        # context.update({'all_data':self.get_all_cleaned_data()})
        context.update({'all_data': self.get_all_cleaned_data()})
        self.choices_dict.update({'all_data': self.get_all_cleaned_data()})
        print(context['all_data'])
        return context

    #def process_step(self, form):
     #   if self.steps == 6:
      #      self.extra_context = {'all_data':self.get_all_cleaned_data()}
       #     return render(self.request, 'pages/WizardFiles/confirmationBarGraph.html', self.extra_context)
        #else:
         #   return
    # template_name = 'pages/selectGraph.html'
    condition_dict = {'BarGraphAxes': barGraphWizard, 'CustomizeBarGraph': barGraphWizard,
                      'CustomizeLineGraph': lineGraphWizard, 'ScatterPlotAxes': scatterPlotWizard,
                      'HistogramAxes': histogramWizard, 'ConfirmBarGraph': barGraphWizard,
                      'HistogramDetails': histogramWizard, 'ConfirmHistogram': histogramWizard,
                      'LineGraphAxes': lineGraphWizard, 'PieChartData': pieChartWizard,
                      'PieChartDetails': pieChartWizard, 'ConfirmLineGraph': lineGraphWizard,
                      'IndividualStatisticOptions': individualStatisticWizard, 'CustomizeScatterPlot': scatterPlotWizard}

    def done(self, form_list, **kwargs):
        return render(self.request, 'pages/done.html', {'form_data': [form.cleaned_data for form in form_list],
                                                        'selections': self.choices_dict})

    def get_template_names(self):
        return self.TEMPLATES[self.steps.current]

# Used for sending a test email
# def send_test_mail():
# send_mail('Test subject',
#         'This is the message body',
#        'pjknoch55@gmail.com',
#       ['pjknoch@sbcglobal.net'])
