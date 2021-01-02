from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from login.models import CustomUser

# Making this global because it will be reused among multiple
# "reports' forms
DEMOGRAPHICS = [('Ethnicity', 'Ethnicity'),
                ('Career', 'Career'),
                ('Benefit Chapter', 'Benefit Chapter'),
                ('Usage by Date', 'Usage by Date'),
                ('College', 'College'),
                ('Total Usage by Location', 'Total Usage by Location')]

HIST_TIME_CHOICES = [('Time of Day', 'Time of Day'),
                     ('Months', 'Months'),
                     ('Years', 'Years')]


# Base class used for incorporating the password authentication
class CurrentPasswordForm(forms.Form):
    current_password = forms.CharField(label='Enter your password for your account:',
                                       widget=forms.PasswordInput
                                       (attrs={'class': 'form-control', 'placeholder': '******'}))
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CurrentPasswordForm, self).__init__(*args, **kwargs)

    def check_entry(self):
        password = self.data['current_password']
        if not self.user.check_password(password):
            self.add_error('current_password', 'Incorrect Password. Please'
                                               ' enter the correct password for your account.')
            return False
        else:
            return True


# Used for changing the first and/or last name
# Inherits from ChangePassForm and authenticates user before anything
# can be changed
class ChangeNameForm(CurrentPasswordForm):
    attributes_first = {'placeholder': 'Jane', 'class': 'form-control',
                        'name': 'first_name', 'id': 'firstName'}
    attributes_last = {'placeholder': 'Doe', 'class': 'form-control', 'name': 'last_name',
                       'id': 'lastName', 'onchange': 'nonEmptyFields();'}
    first_name = forms.CharField(label='Enter new first name:',
                                 widget=forms.TextInput(attrs=attributes_first), max_length=50)
    last_name = forms.CharField(label='Enter new last name:',
                                widget=forms.TextInput(attrs=attributes_last), max_length=50)

    def __init__(self, *args, **kwargs):
        super(ChangeNameForm, self).__init__(*args, **kwargs)


# Used for changing the email of a user account
# Inherits from ChangePassForm and authenticates user before anything
# can be changed
class ChangeEmailForm(CurrentPasswordForm):
    attributes_email = {'placeholder': 'email@unr.edu', 'class': 'form-control',
                        'name': 'email_addr', 'id': 'NewEmail1'}
    attributes_confirm = {'placeholder': 'email@unr.edu', 'class': 'form-control', 'name': 'email_confirm',
                          'id': 'NewEmail2', 'onchange': 'checkEmailMatch();'}
    email_addr = forms.EmailField(label='Enter new email:',
                                  widget=forms.EmailInput(attrs=attributes_email), max_length=50)
    email_confirm = forms.EmailField(label='Confirm new email:',
                                     widget=forms.EmailInput(attrs=attributes_confirm), max_length=50)

    def __init__(self, *args, **kwargs):
        super(ChangeEmailForm, self).__init__(*args, **kwargs)


class UserProfileForm(CurrentPasswordForm):
    attributes = {'class': 'custom-file-input', 'name': 'prof_pic', 'id': 'prof_change'}
    prof_pic = forms.ImageField(label='Upload Profile Picture:', widget=forms.FileInput(attrs=attributes))

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)


# The first page of the report wizard
# User selects between different types of reports
# (e.g. Bar Graph, Pie Chart, Table)
class SelectReportType(forms.Form):
    CHOICES = [('Bar Graph', 'Bar Graph'),
               ('Histogram', 'Histogram'),
               ('Line Graph', 'Line Graph'),
               ('3D Graph', '3D Graph'),
               ('Pie Chart', 'Pie Chart'),
               ('Scatter Plot', 'Scatter Plot'),
               ('Table', 'Table'),
               ('Individual Statistic', 'Individual Statistic')]
    attributes = {'title': 'I need: '}  # left out form-check-input
    graphType = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(attrs=attributes))

    def __init__(self, *args, **kwargs):
        super(SelectReportType, self).__init__(*args, **kwargs)
        self.fields['graphType'].label = ''


# -- Part of the Reports Wizard --
# If the user selects a bar graph, we want to use this form on the second step
class BarGraphAxes(forms.Form):
    selection = forms.ChoiceField(choices=DEMOGRAPHICS)


# Select the reporting time period
# E.g. total visitors from Jan-March 2019
class TimeFrame(forms.Form):
    # TODO DateInput attrs
    #from_time = forms.DateField(input_formats=['%d/%m/%Y'], widget=forms.DateInput(attrs={'class': 'form-control '
    #                                                                                              'datepicker-input',
     #                                                                                    'id': 'datepicker1'}))
    #to_time = forms.DateField(input_formats=['%d/%m/%Y'], widget=forms.DateInput(attrs={'class': 'form-control '
     #                                                                                           'datepicker-input',
      #                                                                                 'id': 'datepicker2'}))
    from_time = forms.DateField(input_formats=['%m/%d/%Y'], widget=forms.DateInput(format='%m/%d/%Y', attrs={'class': 'form-control '
                                                                                                   'datepicker-input',
                                                                                          'id': 'datepicker1', 'autocomplete':'off'}))

    to_time = forms.DateField(input_formats=['%m/%d/%Y'], widget=forms.DateInput(format='%m/%d/%Y', attrs={'class': 'form-control '
                                                                                                 'datepicker-input',
                                                                                        'id': 'datepicker2', 'autocomplete':'off'}))

# Used for selecting between different places that visitors attend in the VMC
# User selects one or more checkboxes that correspond to locations to track attendance
# for in the report.
class AttendanceDataForm(forms.Form):
    CHOICES = [('Main Office', 'Main Office'),
               ('VMC', 'VMC'),
               ('Some Other Event A', 'Some Other Event A'),
               ('Some Other Event B', 'Some Other Event B')]

    attributes = {'title':'Select Attendance Location:'}

    attendance_data = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple(attrs=attributes))

    select_all = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(AttendanceDataForm, self).__init__(*args, **kwargs)
        self.fields['attendance_data'].label = ''

class CustomizeBarGraph(forms.Form):
    COLOR_CHOICES = [('Red', 'Red'),
                     ('Green', 'Green'),
                     ('Blue', 'Blue'),
                     ('Magenta', 'Magenta'),
                     ('Purple', 'Purple'),
                     ('Orange', 'Orange'),
                     ('Yellow', 'Yellow'),
                     ('Brown', 'Brown'),
                     ('Black', 'Black')]

    Y_N_CHOICES = [('Yes', 'Yes'),
                   ('No', 'No')]

    select_bar_color = forms.ChoiceField(choices=COLOR_CHOICES)

    autoscale = forms.ChoiceField(choices=Y_N_CHOICES, widget=forms.RadioSelect(), label='Automatically scale the '
                                                                                         'count?')

    max_count = forms.IntegerField(widget=forms.NumberInput(), label='Max count to display:')

    increment_by = forms.IntegerField(widget=forms.NumberInput(), label='Increment by:')

# In the wizard, this is used if the user wants to create a histogram.
# The user selects different time periods to track attendance.
class HistogramAxes(forms.Form):
    selection = forms.ChoiceField(choices=HIST_TIME_CHOICES)



