from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from login.models import CustomUser
from visualizations.models import ReportPresets
from .CustomFields import *

# Making this global because it will be reused among multiple
# "reports' forms
DEMOGRAPHICS = [('End Term Semester GPA', 'End Term Semester GPA'),
                ('End Term Cumulative GPA', 'End Term Cumulative GPA'),
                ('End Term Attempted Credits', 'End Term Attempted Credits'),
                ('End Term Earned Credits', 'End Term Earned Credits'),
                ('End Term Cumulative Completed Credits', 'End Term Cumulative Completed Credits'),
                ('Benefit Chapter', 'Benefit Chapter'),
                ('STEM Major', 'STEM Major'),
                ('Residential Distance from Campus', 'Residential Distance from Campus'),
                ('Employment', 'Employment'),
                ('Weekly Hours Worked', 'Weekly Hours Worked'),
                ('Number of Dependents', 'Number of Dependents'),
                ('Marital Status', 'Marital Status'),
                ('Gender Identity', 'Gender Identity'),
                ('Parent Education', 'Parent Education'),
                ('Break in University Attendance', 'Break in University Attendance'),
                ('Pell Grant', 'Pell Grant'),
                ('Needs Based Grants/Scholarships', 'Needs Based Grants/Scholarships'),
                ('Merits Based Grants/Scholarships', 'Merits Based Grants/Scholarships'),
                ('Federal Work Study', 'Federal Work Study'),
                ('Military Grants', 'Military Grants'),
                ('Millennium Scholarship', 'Millennium Scholarship'),
                ('Nevada Pre-Paid', 'Nevada Pre-Paid'),
                ('Best Method of Contact', 'Best Method of Contact'),
                  ('Usage by Date', 'Usage by Date'),
                  ('Total Usage by Location', 'Total Usage by Location'),
                  ('Classification', 'Classification'),
                  ('Major', 'Major'),
                  ('Services', 'Services')]

HIST_TIME_CHOICES = [('Average visitors by time', 'Average visitors by time'),
                     ('Average visitors by day', 'Average visitors by day'),
                     ('Total visitors by day', 'Total visitors by day'),
                     ('Total visitors by year', 'Total visitors by year')]
YES_NO = [('Yes', 'Yes'),
          ('No', 'No')]


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
    email_addr = forms.CharField(label='Enter new email:',
                                  widget=forms.TextInput(attrs=attributes_email))
    email_confirm = forms.CharField(label='Confirm new email:',
                                     widget=forms.TextInput(attrs=attributes_confirm))

    def clean_email_confirm(self):
        data = self.cleaned_data['email_confirm']

        if '@' in data:
            raise ValidationError('Email should not contain "@" and must be a valid UNR email name.')



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
               ('Line and/or Scatter', 'Line and/or Scatter'),
               ('Pie Chart', 'Pie Chart'),
               ('Individual Statistic', 'Individual Statistic')]
    attributes = {'title': 'I need: '}  # left out form-check-input
    graphType = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(attrs=attributes))
    custom_title = forms.ChoiceField(choices=YES_NO, widget=forms.RadioSelect(attrs={'id': 'custom_title'}))
    title = forms.CharField(widget=forms.TextInput(attrs={'id':'title'}), required=False)

    def __init__(self, *args, **kwargs):
        super(SelectReportType, self).__init__(*args, **kwargs)
        self.fields['graphType'].label = ''

    def clean(self):
        data = self.cleaned_data

        if data.get('custom_title') == 'No':
            return data
        elif data.get('custom_title') == 'Yes' and data.get('title') != '':
            return data
        else:
            raise forms.ValidationError(
                'Enter name for \'Title\' or change \'Custom title\' to \'No\'.')


# -- Part of the Reports Wizard --
# If the user selects a bar graph, we want to use this form on the second step
class BarGraphAxes(forms.Form):
    TIME_VS_COMPARISONS = [('Count visits over time', 'Count visits over time'),
                           ('Compare GPA against demographics', 'Compare GPA against demographics')]

    DEMO = [
        ('Benefit Chapter', 'Benefit Chapter'),
        ('Residential Distance from Campus', 'Residential Distance from Campus'),
        ('Employment', 'Employment'),
        ('Weekly Hours Worked', 'Weekly Hours Worked'),
        ('Number of Dependents', 'Number of Dependents'),
        ('Marital Status', 'Marital Status'),
        ('Gender Identity', 'Gender Identity'),
        ('Parent Education', 'Parent Education'),
        ('Break in University Attendance', 'Break in University Attendance'),
        ('Pell Grant', 'Pell Grant'),
        ('Needs Based Grants/Scholarships', 'Needs Based Grants/Scholarships'),
        ('Merits Based Grants/Scholarships', 'Merits Based Grants/Scholarships'),
        ('Federal Work Study', 'Federal Work Study'),
        ('Military Grants', 'Military Grants'),
        ('Millennium Scholarship', 'Millennium Scholarship'),
        ('Nevada Pre-Paid', 'Nevada Pre-Paid'),
        ('Best Method of Contact', 'Best Method of Contact'),
        ('Classification', 'Classification'),
        ('Major', 'Major'),
        ('Services', 'Services')
    ]

    GPA_COMPARISON = [('Average end term Semester GPA', 'Average end term Semester GPA'),
                      ('Average end term Cumulative GPA', 'Average end term Cumulative GPA'),
                       ('Average end term Attempted Credits', 'Average end term Attempted Credits'),
                      ('Average end term Earned Credits', 'Average end term Earned Credits'),
                      ('Average end term Cumulative Completed Credits', 'Average end term Cumulative Completed Credits')]

    selection = forms.ChoiceField(choices=DEMOGRAPHICS, required=False)

    include_table = forms.ChoiceField(choices=YES_NO, widget=forms.RadioSelect())

    report_type = forms.ChoiceField(choices=TIME_VS_COMPARISONS, initial='Count visits over time', widget=forms.RadioSelect())

    category = forms.ChoiceField(choices=DEMO, required=False)

    gpa_to_compare = forms.ChoiceField(choices=GPA_COMPARISON, required=False)

    def __init__(self, *args, **kwargs):
        super(BarGraphAxes, self).__init__(*args, **kwargs)
        self.fields['include_table'].label = 'Include table?'

class PieChartCategories(BarGraphAxes):
    report_type = None
    category = None
    gpa_to_compare = None


# Select the reporting time period
# E.g. total visitors from Jan-March 2019
class TimeFrame(forms.Form):
    # TODO DateInput attrs
    # from_time = forms.DateField(input_formats=['%d/%m/%Y'], widget=forms.DateInput(attrs={'class': 'form-control '
    #                                                                                              'datepicker-input',
    #                                                                                    'id': 'datepicker1'}))
    # to_time = forms.DateField(input_formats=['%d/%m/%Y'], widget=forms.DateInput(attrs={'class': 'form-control '
    #                                                                                           'datepicker-input',
    #                                                                                 'id': 'datepicker2'}))
    from_time = forms.DateField(input_formats=['%m/%d/%Y'],
                                widget=forms.DateInput(format='%m/%d/%Y', attrs={'class': 'form-control '
                                                                                          'datepicker-input',
                                                                                 'id': 'datepicker1',
                                                                                 'autocomplete': 'off',
                                                                                 'name': 'from_time'}))

    to_time = forms.DateField(input_formats=['%m/%d/%Y'],
                              widget=forms.DateInput(format='%m/%d/%Y', attrs={'class': 'form-control '
                                                                                        'datepicker-input',
                                                                               'id': 'datepicker2',
                                                                               'autocomplete': 'off',
                                                                               'name': 'to_time'}))

    def clean(self):
        data = self.cleaned_data

        if data.get('from_time') > data.get('to_time'):
            raise forms.ValidationError(
                'The starting date you entered is later than the ending date.')


class HistogramHours(forms.Form):
    from_time = forms.TimeField(input_formats=['%H:%M %p'],
                                widget=forms.TimeInput(format='%H:%M %p',
                                                       attrs={'name': 'timepicker',
                                                              'class': 'timepicker form-control timepicker-input'}))

    to_time = forms.TimeField(input_formats=['%H:%M %p'],
                              widget=forms.TimeInput(format='%H:%M %p',
                                                     attrs={'name': 'timepicker',
                                                            'class': 'timepicker form-control timepicker-input'}))


# Used for selecting between different places that visitors attend in the VMC


# User selects one or more checkboxes that correspond to locations to track attendance
# for in the report.
class AttendanceDataForm(forms.Form):
    CHOICES = [('Veteran Services VMC', 'VMC'),
               ('Veteran Services Fitzgerald', 'Fitzgerald'),
               ('Veteran Services Event', 'Event')]

    attributes = {'title': 'Select Attendance Location:', 'class': 'Locations'}

    attendance_data = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple(attrs=attributes))

    use_custom_event_name = forms.ChoiceField(choices=YES_NO, widget=forms.RadioSelect(attrs={'id':'use_cust_name'}),
                                              required=False)

    custom_event_name = forms.CharField(widget=forms.TextInput(attrs={'id': 'cust_name'}), required=False)


    select_all = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(AttendanceDataForm, self).__init__(*args, **kwargs)
        self.fields['attendance_data'].label = ''


# Allows the user to customize the bar graph
# Such as visuals and additional details regarding axes
class CustomizeBarGraph(forms.Form):
    # Bar color options
    COLOR_CHOICES = [('Red', 'Red'),
                     ('Green', 'Green'),
                     ('Blue', 'Blue'),
                     ('Magenta', 'Magenta'),
                     ('Purple', 'Purple'),
                     ('Orange', 'Orange'),
                     ('Yellow', 'Yellow'),
                     ('Brown', 'Brown'),
                     ('Black', 'Black')]

    # Yes/No choice if user wants to automatically scale the count
    Y_N_CHOICES = [('Yes', 'Yes'),
                   ('No', 'No')]

    # Choice field (dropdown) for selecting the bar color
    select_bar_color = forms.ChoiceField(choices=COLOR_CHOICES)

    # Choice field (checkbox) for toggling autoscale
    autoscale = forms.ChoiceField(choices=Y_N_CHOICES, widget=forms.RadioSelect(attrs={'id': 'autoscale'}),
                                  label='Automatically scale the '
                                        'count?')
    # Integer field for scaling the count
    max_count = forms.IntegerField(widget=forms.NumberInput(attrs={'id': 'max_count'}),
                                   label='Max count to display:', required=False)
    # Integer field for allowing user to customize incrementation
    increment_by = forms.IntegerField(widget=forms.NumberInput(attrs={'id': 'increment_by'}),
                                      label='Increment by:', required=False)

    show_multiple_bars_by_location = forms.ChoiceField(choices=Y_N_CHOICES,
                                                       widget=forms.RadioSelect(attrs={'id': 'grouped_graph'}))

    def clean(self):
        data = self.cleaned_data
        print(data.get('max_count', '1'))

        if data.get('autoscale') == 'Yes':
            return data
        elif data.get('autoscale') == 'No' and (data.get('max_count') and data.get('increment_by')) is not None:
            return data
        else:
            raise forms.ValidationError(
                'Enter values for \'Max Count\' and \'Increment by\' or change autoscale to \'Yes\'.')


# Line Graph customization is the same as bar graph customization, except the user
# is selecting 'line color' instead of bar color
class CustomizeLineGraph(CustomizeBarGraph):
    select_bar_color = None  # Override this field to not show anything

    # Instead, label is "select line color"

    select_line_color = forms.ChoiceField(choices=CustomizeBarGraph.COLOR_CHOICES)

    # Integer field for scaling the count
    max_count = forms.IntegerField(widget=forms.NumberInput(attrs={'id': 'line_max'}),
                                   label='Max count to display:', required=False)
    # Integer field for allowing user to customize incrementation
    increment_by = forms.IntegerField(widget=forms.NumberInput(attrs={'id': 'line_increment'}),
                                      label='Increment by:', required=False)

    show_multiple_bars_by_location = None


# In the wizard, this is used if the user wants to create a histogram.
# The user selects different time periods to track attendance.
class HistogramAxes(forms.Form):
    selection = None

    time_units = forms.ChoiceField(choices=HIST_TIME_CHOICES)

    include_table = forms.ChoiceField(choices=YES_NO, widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):
        super(HistogramAxes, self).__init__(*args, **kwargs)
        self.fields['include_table'].label = 'Include table? '


# Detailed options for the histogram wizard
class HistogramDetails(CustomizeBarGraph):
    attributes_for_data_options = {'title': 'Select Data Options:'}
    attributes_for_attendance_data = {'title': 'Select Attendance Location(s)'}

    # Integer field for scaling the count
    max_count = forms.IntegerField(widget=forms.NumberInput(attrs={'id': 'hist_max'}),
                                   label='Max count to display:', required=False)
    # Integer field for allowing user to customize incrementation
    increment_by = forms.IntegerField(widget=forms.NumberInput(attrs={'id': 'hist_increment'}),
                                      label='Increment by:', required=False)

    show_multiple_bars_by_location = None


# Wizard form that allows the user to customize the pie chart
# The user can display data in the form of: percentages, count, or both
class PieChartDetails(forms.Form):
    # Percentages, count, or both
    DATA_OPTIONS = [('Percent of total', 'Percent of total'),
                    ('Count', 'Count'),
                    ('Both percentages and count', 'Both percentages and count')]
    # Radio buttons for the data display options
    Data_units = forms.ChoiceField(choices=DATA_OPTIONS, widget=forms.RadioSelect())


# Scatter Plot customization is the same as bar graph customization, except the user
# is selecting 'dot color' instead of 'bar color'
# Inherits from form CustomizeBarGraph
class CustomizeScatterPlot(CustomizeBarGraph):
    # Dot color options
    select_bar_color = None

    OPTIONS = [('Dots', 'Dots'),
               ('Lines', 'Lines'),
               ('Dots and Lines', 'Dots and Lines')]

    # Instead, label is "select dot color"
    # Reuse same color choices as bar graph
    select_dot_color = forms.ChoiceField(choices=CustomizeBarGraph.COLOR_CHOICES)

    # Integer field for scaling the count
    max_count = forms.IntegerField(widget=forms.NumberInput(attrs={'id': 'scatter_max'}),
                                   label='Max count to display:', required=False)
    # Integer field for allowing user to customize incrementation
    increment_by = forms.IntegerField(widget=forms.NumberInput(attrs={'id': 'scatter_increment'}),
                                      label='Increment by:', required=False)

    display_as = forms.ChoiceField(choices=OPTIONS)

    show_multiple_bars_by_location = None


# Individual statistic counting/tracking options
# Options are similar to the 'axes' options, except the user may
# want to keep track of averages or percentages instead of total count
class IndividualStatisticOptions(BarGraphAxes):
    report_type = None
    category = None
    gpa_to_compare = None

    COUNT_OPTIONS = [('Total Count', 'Total Count'),
                     ('Daily average', 'Daily average'),
                     ('Monthly average', 'Monthly average'),
                     ('Yearly average', 'Yearly average')]

    count_options = forms.ChoiceField(choices=COUNT_OPTIONS)

    def __init__(self, *args, **kwargs):
        super(IndividualStatisticOptions, self).__init__(*args, **kwargs)
        del self.fields['include_table']


# Details for individual statistics
# User can change label font (size and/or color),
# statistic font (size and/or color)
class IndividualStatisticDetails(forms.Form):
    # Color options
    # Bar color options
    COLOR_CHOICES = [('Red', 'Red'),
                     ('Green', 'Green'),
                     ('Blue', 'Blue'),
                     ('Magenta', 'Magenta'),
                     ('Purple', 'Purple'),
                     ('Orange', 'Orange'),
                     ('Yellow', 'Yellow'),
                     ('Brown', 'Brown'),
                     ('Black', 'Black')]
    # Choices for font size
    # TODO user can also customize input
    FONT_CHOICES = [('8', '8'),
                    ('10', '10'),
                    ('12', '12'),
                    ('14', '14'),
                    ('16', '16'),
                    ('18', '18'),
                    ('20', '20'),
                    ('24', '24'),
                    ('28', '28'),
                    ('32', '32'),
                    ('36', '36'),
                    ('42', '42'),
                    ('48', '48'),
                    ('72', '72')]
    header_font_color = forms.ChoiceField(choices=COLOR_CHOICES)
    statistic_font_color = forms.ChoiceField(choices=COLOR_CHOICES)
    header_font_size = forms.ChoiceField(choices=FONT_CHOICES)
    statistic_font_size = forms.ChoiceField(choices=FONT_CHOICES)


class ReportPresetName(forms.Form):
    attributes = {'id': 'preset_input', 'name': 'preset_input', 'class': 'form-control'}

    enter_preset_name = forms.CharField(widget=forms.TextInput(attrs=attributes))

    def check_entry(self):
        name = self.data['enter_preset_name']
        if ReportPresets.objects.filter(pk=name).exists():
            self.add_error('enter_preset_name',
                           'This preset with the name ' + name + ' already exists. Please choose a different name.')
            return False
        else:
            return True
