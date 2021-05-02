import sys

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.http import urlsafe_base64_decode

from login.models import CustomUser
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import update_session_auth_hash, logout, login, tokens
from formtools.wizard.views import SessionWizardView
from .forms import *
from visualizations.models import ReportPresets
from datetime import datetime
from urllib.parse import quote

# Forms for the Reports Wizard
FORMS = [('SelectReportType', SelectReportType),
         ('BarGraphAxes', BarGraphAxes),
         ('LineGraphAxes', BarGraphAxes),
         ('HistogramAxes', HistogramAxes),
         ('PieChartData', PieChartCategories),
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
         ('ConfirmBarGraph', forms.Form),  # Just use the default Django form class for these,
         ('ConfirmHistogram', forms.Form),  # since we are not asking for any input
         ('ConfirmLineGraph', forms.Form),
         ('ConfirmPieChart', forms.Form),
         ('ConfirmScatterPlot', forms.Form),
         ('ConfirmIndividualStatistic', forms.Form)]

# Temporarily store wizard choices if the user wants to save a "preset"
preset_storage = {}


def manualPageView(request):
    if(request.method == 'POST'):
        print(request.POST)
    return HttpResponse('Survey data recorded.');

def surveyPageView(request):
    if(request.method == 'GET'):
        return render(request, 'pages/survey.html')
    if(request.method == 'POST'):
        #mystr = '';
        if(len(list(request.POST.items())) != 22):
            #return HttpResponse(list(request.POST.items()));
            return render(request, 'pages/survey.html'); #Did not fill out entire form
        #Connect to DB
        import sqlite3
        conn = sqlite3.connect('vmc_tap.db');

	#Check if student exists
        #student_exists = [];
        get_student = "SELECT COUNT(student_id) FROM demographics WHERE student_id = " + str(request.POST["student_id"]) + ";";
        for d in conn.execute(get_student):
            student_exists = d[0];
        mystr = '@' + str(student_exists) + '@';
        
        query_names = ['student_name', 'student_id', 'benefit_chapter', 'is_stem', 'currently_live', 'employment', 'work_hours', 'dependents', 'marital_status', 'gender', 'parent_education', 'break_in_attendance', 'pell_grant', 'needs_based', 'merit_based', 'federal_work_study', 'military_grants', 'millennium_scholarship', 'nevada_prepaid', 'contact_method'];
        query_values = [request.POST["first_name"] + ' ' + request.POST["last_name"]];
        query_values.extend([request.POST[a] for a in query_names if a != 'student_name']);
        #Student not not yet exist
        if(student_exists == 0):
            sql_statement = "INSERT INTO demographics (" + ",".join(query_names) + ") VALUES (" + ",".join(['\'' + str(a) + '\'' for a in query_values]) + ");";

        #Student does exist
        else:
            query_commas = [', ',', ',', ',', ',', ',', ',', ',', ',', ',', ',', ',', ',', ',', ',', ',', ',', ',', ',', ',' '];
            sql_statement = "UPDATE demographics SET student_name = '" + request.POST["first_name"] + ' ' + request.POST["last_name"] + "', ";
            for i, name in enumerate(query_names):
                if(name != 'student_name'):
                    sql_statement += name + ' = \'' + query_values[i] + '\'' + query_commas[i];
            sql_statement += 'WHERE student_id = ' + str(request.POST["student_id"]) + ';';
        conn.execute(sql_statement);
        conn.commit();

        conn.close();
    return render(request, 'pages/surveyThanks.html')
    #return HttpResponse('Survey data recorded.');

def homePageView(request):
    if request.user.is_authenticated:
        return render(request, 'pages/homePage.html')
    else: 
        return redirect('login')


def importPageView(request):
    # if request.method == 'POST': #This if statement is not needed, the import page will never have a load condition with a 'POST' method. Leaving for reference reasons
    #     return HttpResponseRedirect('/parse')
    # return render(request, 'pages/importPage.html')

    if request.user.is_authenticated:
        return render(request, 'pages/importPage.html')
    else: 
        return redirect('login')

def importGPAView(request):
    if request.method == 'POST':
        return HttpResponseRedirect('/parse/gpa')
    return render(request, 'pages/importGPAPage.html')


# Render the admin page
def vmcAdminPageView(request):
    if request.user.is_authenticated:
        return render(request, "pages/vmcAdminPage.html")
    else: 
        return redirect('login')

# Render the main reports page
def visPageView(request):
    if request.user.is_authenticated:
        return render(request, 'pages/visualizationsPage.html')
    else: 
        return redirect('login')

# Allow users to change their password
# Renders the form for changing passwords
def changePassView(request, emailAddress):
    if request.user.is_authenticated:
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
    else: 
        return redirect('login')


# Allow users to change their email
def changeEmailView(request, email):
    if request.user.is_authenticated:
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
                    user.email += '@unr.edu'
                    user.save()
                    saved_user.delete()
                    login(request, user)
                else:

                    old_user_email = user.email
                    user.email = request.POST.get('email_confirm')
                    user.email += '@unr.edu'
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
    else: 
        return redirect('login')

# Renders the HTML page that allows users to upload/change their profile picture
def changeProfileView(request):
    if request.user.is_authenticated:
        return render(request, 'pages/changeProfilePage.html')
    else: 
        return redirect('login')

# Renders the HTML page that displays user accounts
def viewAccountsList(request):
    if request.user.is_authenticated:
        return render(request, 'pages/viewAccountsList.html')
    else: 
        return redirect('login')

# Helper function for obtaining all user accounts from the database
def accessAccounts():
    users = CustomUser.objects.all()
    return users

# Helper function for obtaining individual user accounts
# primary key = user email address (unique to each user)
def accessIndividualAccount(emailAddress):
    user = CustomUser.objects.get(pk=emailAddress)
    return user

# Helper function for flattening a list
def flatten(sqlList):
    flattened_list = []
    for listItems in sqlList:
        for item in listItems:
            flattened_list.append(item)

    return flattened_list

# Renders the HTML page that displays the user accounts
# Only accessible if user is logged in/authenticated
def accountsView(request):
    if request.user.is_authenticated:
        accountsList = accessAccounts()
        emails = []
    
        for user in accountsList:
            emails.append(user.email)
    
        return render(request, 'pages/viewAccountsList.html', {'emails': emails})
    # Redirect to login page if user is not logged in
    else: 
        return redirect('login')

# Renders the HTML page that displays the account options for an individual user
def otherAccountOptions(request, emailAddress):
    # If the user is logged in
    if request.user.is_authenticated:
        # Get the user account information from the database
        userAccount = accessIndividualAccount(emailAddress)

        info = {'accountName': userAccount.email, 'firstName': userAccount.first_name, 'lastName': userAccount.last_name}
        return render(request, 'pages/individualAccountOption.html', info)
    # Redirect to the login page if the user is not authenticated
    else: 
        return redirect('login')

# Renders the HTML form for creating a new user account
def newAccount(request):
    # If the user submits the form
    if request.method == 'POST':
        import hashlib
        import sqlite3
        # Get account information, such as first name, last name, email address, and password
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        email = request.POST.get('email')
        # Must have @unr.edu email address
        email += '@unr.edu'
        password = request.POST.get('password')
        CustomUser.objects.create_superuser(email, first_name, last_name, password)
        return render(request, 'pages/accountCreated.html', {'email': email})
    return render(request, 'pages/newAccount.html')

# Renders the HTML form that shows the user that the account was successfully deleted
def deleteAccount(request, emailAddress):
    # If the user is logged in
    if request.user.is_authenticated:
        # Get the user object from the database
        user = CustomUser.objects.get(pk=emailAddress)
        # Delete the user object from the database
        user.delete()

        return render(request, 'pages/accountDeleted.html', {'email': emailAddress})
    # Redirect to the login page
    else: 
        return redirect('login')    

# Renders the HTML page when a new user account is sucessfully created
def accountCreated(request, emailAddress):
    # If the user is logged in
    if request.user.is_authenticated:
        # Get the individual user account from the database
        accountList = accessIndividualAccount(emailAddress)
        # Get the email address from the user account object
        email = accountList.email

        return render(request, 'pages/individualAccountOption.html', {'email': email})
    else: 
        return redirect('login') 

# Renders the HTML page for resetting the password when the user is not authenticated/logged in
def PassReset(request):
    if request.method == 'POST':
        # Get the user's email address
        email = request.POST.get('email')
        form = PasswordResetForm(request.POST)
        # If the email address is valid
        if form.is_valid():
            form.save(request=request)
            return render(request, 'pages/emailSent.html', {'email': email})

    return render(request, 'pages/forgotPassword.html')

# When the user requests a password reset email, they receive a one-time link in the email
# The ChangePass view ensures that the link is still valid directs the user to change their
# password if the link is valid; otherwise, the user is given an error message
def ChangePass(request, uidb64, token):
    # Decode the password reset link
    email = urlsafe_base64_decode(uidb64).decode()
    # Get the user object from the database
    user = CustomUser.objects.get(pk=email)
    # Check to see if the password reset link is still valid
    tokenChecker = tokens.PasswordResetTokenGenerator()
    # If the token is still valid, allow the user to change their password
    if tokenChecker.check_token(user, token):
        login(request, user)
    # Otherwise, raise an HTTP 404 error message to inform the user that the link is still invalid
    else:
        raise Http404('Password reset link is no longer valid. Please get another email.')

    return render(request, 'pages/passResetConfirm.html')


# After the user has change their password, log them out and return to the login page
def successfullyChangedPass(request):
    # After the user submits the new password (clicks the "submit" button)
    if request.method == 'POST':
        # Get the new password, hash it, and updated it
        request.user.set_password(request.POST.get('newPassword2'))
        update_session_auth_hash(request, request.user)
        email = request.user.email
        # Save the new password into the database, then log the user back out because
        # they requested the password reset while they were not authenticated (via email password reset)
        request.user.save()
        logout(request)

    return render(request, 'pages/passChangeSuccess.html', {'email': email})

# Allow the user to change their first and last name
# Renders the HTML form that shows the user that they successfully changed their
# first/last name
def changeName(request, accountName):
    if request.user.is_authenticated:
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
    else: 
        return redirect('login')  


def profileImageView(request, accountName):
    if request.user.is_authenticated:
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
    else: 
        return redirect('login')


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
    return conditionalWizardBranch(wizard, 'Line and/or Scatter')


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
    TEMPLATES = {'SelectReportType': 'pages/WizardFiles/selectGraph.html',
                 'BarGraphAxes': 'pages/WizardFiles/barGraphAxes.html',
                 'LineGraphAxes': 'pages/WizardFiles/barGraphAxes.html',
                 'HistogramAxes': 'pages/WizardFiles/histogramFreq.html',
                 'ScatterPlotAxes': 'pages/WizardFiles/barGraphAxes.html',
                 'PieChartData': 'pages/WizardFiles/pieChartCategories.html',
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
                 'ConfirmHistogram': 'pages/WizardFiles/confirmHistogram.html',
                 'ConfirmLineGraph': 'pages/WizardFiles/confirmLineGraph.html',
                 'ConfirmPieChart': 'pages/WizardFiles/confirmPieChart.html',
                 'ConfirmScatterPlot': 'pages/WizardFiles/confirmScatterPlot.html',
                 'ConfirmIndividualStatistic': 'pages/WizardFiles/confirmIndividualStatistic.html'}

    def get_context_data(self, form, **kwargs):
        context = super(ReportWizardBase, self).get_context_data(form=form, **kwargs)
        context.update({'all_data': self.get_all_cleaned_data()})
        self.choices_dict.update({'all_data': self.get_all_cleaned_data()})
        return context

    condition_dict = {'BarGraphAxes': barGraphWizard, 'CustomizeBarGraph': barGraphWizard,
                      'CustomizeLineGraph': lineGraphWizard, 'ScatterPlotAxes': scatterPlotWizard,
                      'HistogramAxes': histogramWizard, 'ConfirmBarGraph': barGraphWizard,
                      'HistogramDetails': histogramWizard, 'ConfirmHistogram': histogramWizard,
                      'ConfirmPieChart': pieChartWizard, 'IndividualStatisticDetails': individualStatisticWizard,
                      'LineGraphAxes': lineGraphWizard, 'PieChartData': pieChartWizard,
                      'PieChartDetails': pieChartWizard, 'ConfirmLineGraph': lineGraphWizard,
                      'IndividualStatisticOptions': individualStatisticWizard,
                      'CustomizeScatterPlot': scatterPlotWizard,
                      'ConfirmScatterPlot': scatterPlotWizard, 'ConfirmIndividualStatistic': individualStatisticWizard}

    # This function is called after the user is done with the wizard
    def done(self, form_list, **kwargs):
        global preset_storage

        preset_name_form = ReportPresetName()
        data = {'form_data': [form.cleaned_data for form in form_list], 'form': preset_name_form}
        preset_storage = {'form_data': [form.cleaned_data for form in form_list]}
        # If the user wants to save their report presets (except for date)
        if self.request.POST.get('save'):
            return render(self.request, 'pages/WizardFiles/savePreset.html',
                          data) #'selections': self.choices_dict, 'form':form})
        #elif self.request.POST.get('')
        # If the user does not want to save their report presets
        else:
            return render(self.request, 'pages/done.html', data)
                                                           # 'selections': self.choices_dict})

    def get_template_names(self):
        return self.TEMPLATES[self.steps.current]

def savePreset(request):
    if request.user.is_authenticated:
        presets = ReportPresets.objects.filter(user=request.user)
        if len(presets) <= 14:
            if request.method == 'POST':
                form = ReportPresetName(request.POST)
                if form.check_entry():
                    name = request.POST.get('enter_preset_name')
                    saveChoices(request, name)
                else:
                    return render(request, 'pages/wizardFiles/savePreset.html',
                                {'form': form})
    
    
            return render(request, 'pages/WizardFiles/presetSaved.html', {'name': name})
        else:
            return render(request, 'pages/sizeLimitReached.html')
    else: 
        return redirect('login')

def locationInserter(loc_list):
    loc_string = ''
    for location in loc_list:
        if location != loc_list[-1]:
            loc_string += location + ','
        else:
            loc_string += location

    return loc_string


def saveChoices(request, name):
    global preset_storage
    preference = ReportPresets()
    inner_dict = preset_storage['form_data']
    graph_type = inner_dict[0]
    cust_title = graph_type['title']

    if graph_type['graphType'] == 'Bar Graph':
        sel_dict = inner_dict[1]
        selection = sel_dict['selection']
        incl_table = sel_dict['include_table']
        report_type = sel_dict['report_type']
        category = sel_dict['category']
        gpa_to_compare = sel_dict['gpa_to_compare']
        customization = inner_dict[3]
        sel_bar_color = customization['select_bar_color']
        autoscale = customization['autoscale']
        max_ct = customization['max_count']
        inc_by = customization['increment_by']
        mult_bars = customization['show_multiple_bars_by_location']

        loc_dict = inner_dict[4]
        loc = loc_dict['attendance_data']
        loc = locationInserter(loc)
        sel_all = loc_dict['select_all']
        use_custom_event_name = loc_dict['use_custom_event_name']
        custom_event_name = loc_dict['custom_event_name']

        Preset = ReportPresets(graph_type=graph_type['graphType'], report_type=report_type, category=category,
                               gpa_to_compare=gpa_to_compare, title=cust_title, select_all=sel_all, selection=selection,
                               include_table=incl_table, select_bar_color=sel_bar_color, multiple_bars=mult_bars,
                               autoscale=autoscale, max_count=max_ct, increment_by=inc_by, locations=loc, user=request.user,
                               use_custom_event_name=use_custom_event_name, custom_event_name=custom_event_name,
                               preset_name=name)
        Preset.save()
    elif graph_type['graphType'] == 'Histogram':
        sel_dict = inner_dict[1]
        time_units = sel_dict['time_units']
        incl_tabe = sel_dict['include_table']
        customization = inner_dict[3]
        sel_bar_color = customization['select_bar_color']
        autoscale = customization['autoscale']
        max_ct = customization['max_count']
        inc_by = customization['increment_by']

        loc_dict = inner_dict[4]
        loc = loc_dict['attendance_data']
        loc = locationInserter(loc)
        sel_all = loc_dict['select_all']
        use_custom_event_name = loc_dict['use_custom_event_name']
        custom_event_name = loc_dict['custom_event_name']

        Preset = ReportPresets(graph_type=graph_type['graphType'], title=cust_title, select_all=sel_all,
                               time_units=time_units, include_table=incl_tabe, select_bar_color=sel_bar_color,
                               autoscale=autoscale, max_count=max_ct, increment_by=inc_by, locations=loc,
                               user=request.user, preset_name=name, use_custom_event_name=use_custom_event_name,
                               custom_event_name=custom_event_name)
        Preset.save()
    elif graph_type['graphType'] == 'Line Graph':
        sel_dict = inner_dict[1]
        selection = sel_dict['selection']
        incl_table = sel_dict['include_table']
        customization = inner_dict[3]
        autoscale = customization['autoscale']
        max_ct = customization['max_count']
        inc_by = customization['increment_by']
        sel_line_color = customization['select_line_color']

        loc_dict = inner_dict[4]
        loc = loc_dict['attendance_data']
        loc = locationInserter(loc)
        sel_all = loc_dict['select_all']
        use_custom_event_name = loc_dict['use_custom_event_name']
        custom_event_name = loc_dict['custom_event_name']

        Preset = ReportPresets(graph_type=graph_type['graphType'], title=cust_title, select_all=sel_all,
                               selection=selection, include_table=incl_table, autoscale=autoscale, max_count=max_ct,
                               increment_by=inc_by, line_color=sel_line_color, locations=loc, preset_name=name,
                               user=request.user, use_custom_event_name=use_custom_event_name,
                               custom_event_name=custom_event_name)
        Preset.save()
    elif graph_type['graphType'] == 'Pie Chart':
        sel_dict = inner_dict[1]
        selection = sel_dict['selection']
        incl_table = sel_dict['include_table']

        data_units_dict = inner_dict[3]
        data_units = data_units_dict['Data_units']

        loc_dict = inner_dict[4]
        loc = loc_dict['attendance_data']
        loc = locationInserter(loc)
        sel_all = loc_dict['select_all']
        use_custom_event_name = loc_dict['use_custom_event_name']
        custom_event_name = loc_dict['custom_event_name']

        Preset = ReportPresets(graph_type=graph_type['graphType'], title=cust_title, select_all=sel_all,
                               selection=selection, include_table=incl_table, data_units=data_units, locations=loc,
                               preset_name=name, user=request.user, use_custom_event_name=use_custom_event_name,
                               custom_event_name=custom_event_name)
        Preset.save()
    elif graph_type['graphType'] == 'Line and/or Scatter':
        sel_dict = inner_dict[1]
        selection = sel_dict['selection']
        incl_table = sel_dict['include_table']

        report_type = sel_dict['report_type']
        category = sel_dict['category']
        gpa_to_compare = sel_dict['gpa_to_compare']

        customization = inner_dict[3]
        autoscale = customization['autoscale']
        max_ct = customization['max_count']
        inc_by = customization['increment_by']
        sel_dot_color = customization['select_dot_color']

        loc_dict = inner_dict[4]
        loc = loc_dict['attendance_data']
        loc = locationInserter(loc)
        sel_all = loc_dict['select_all']
        use_custom_event_name = loc_dict['use_custom_event_name']
        custom_event_name = loc_dict['custom_event_name']

        Preset = ReportPresets(graph_type=graph_type['graphType'], report_type=report_type, category=category,
                               gpa_to_compare=gpa_to_compare, title=cust_title, selection=selection,
                               select_all=sel_all, include_table=incl_table, autoscale=autoscale, max_count=max_ct,
                               increment_by=inc_by, dot_color=sel_dot_color, locations=loc, preset_name=name,
                               user=request.user, use_custom_event_name=use_custom_event_name,
                               custom_event_name=custom_event_name)
        Preset.save()
    elif graph_type['graphType'] == 'Individual Statistic':
        sel_dict = inner_dict[1]
        selection = sel_dict['selection']
        count_options = sel_dict['count_options']

        customization = inner_dict[3]
        label_color = customization['header_font_color']
        statistic_font_color = customization['statistic_font_color']
        statistic_font_size = customization['statistic_font_size']
        label_font_size = customization['header_font_size']

        loc_dict = inner_dict[4]
        loc = loc_dict['attendance_data']
        loc = locationInserter(loc)
        sel_all = loc_dict['select_all']
        use_custom_event_name = loc_dict['use_custom_event_name']
        custom_event_name = loc_dict['custom_event_name']

        Preset = ReportPresets(graph_type=graph_type['graphType'], title=cust_title, selection=selection,
                               count_options=count_options, header_font_color=label_color,
                               statistic_font_color=statistic_font_color, statistic_font_size=statistic_font_size,
                               header_font_size=label_font_size, select_all=sel_all, locations=loc, preset_name=name,
                               user=request.user, use_custom_event_name=use_custom_event_name,
                               custom_event_name=custom_event_name)
        Preset.save()


def reportsView(request):
    if request.user.is_authenticated:
        return render(request, 'pages/reportsPage.html')
    else: 
        return redirect('login')
    

def viewPresets(request):
    if request.user.is_authenticated:
        presets = ReportPresets.objects.filter(user=request.user)
        return render(request, 'pages/viewPresets.html', {'presets': presets})
    else: 
        return redirect('login')

def individualPresetOptions(request, name):
    if request.user.is_authenticated:
        preset = ReportPresets.objects.get(pk=name)
        #print(preset.selection)

        return render(request, 'pages/individualPresetOptions.html', {'name': name, 'preset':preset})
    else: 
        return redirect('login')

def deletePreset(request, name):
    if request.user.is_authenticated:
        preset = ReportPresets.objects.get(pk=name)
        preset.delete()

        return render(request, 'pages/deletePreset.html', {'name': name})
    else: 
        return redirect('login')

def createReportFromPreset(request, name):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = TimeFrame(request.POST)

            if form.is_valid():
                from_time = request.POST.get('from_time')
                to_time = request.POST.get('to_time')

                from_time = datetime.strptime(from_time, '%m/%d/%Y')
                to_time = datetime.strptime(to_time, '%m/%d/%Y')

                from_time = from_time.strftime('%m-%d-%Y')
                to_time = to_time.strftime('%m-%d-%Y')

                name = quote(name)
                print('url encoded name:', name)

                # Generate report here
                return render(request, 'pages/presetReportGenerated.html', {'preset_name': name,
                                                                            'from_time': from_time, 'to_time': to_time,
                                                                            'form': form})
            else:
                return render(request, 'pages/createReportFromPreset.html', {'form': form})
        else:
            form = TimeFrame()
            return render(request, 'pages/createReportFromPreset.html', {'name': name, 'form':form})
    else: 
        return redirect('login')


