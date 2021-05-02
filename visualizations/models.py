from django.db import models

# Database tables for saving user report preferences
# Visit period is not included (the user will generally select
# new dates for the same graph preferences)
from login.models import CustomUser



class ReportPresets(models.Model):
    # Choices for 'selection' field
    DEMOGRAPHICS = [('Ethnicity', 'Ethnicity'),
                    ('Career', 'Career'),
                    ('Benefit Chapter', 'Benefit Chapter'),
                    ('Usage by Date', 'Usage by Date'),
                    ('College', 'College'),
                    ('Total Usage by Location', 'Total Usage by Location')]

    # Time choices for Histogram 'time interval' field
    HIST_TIME_CHOICES = [('Time of Day', 'Time of Day'),
                         ('Months', 'Months'),
                         ('Years', 'Years')]
    # Autoscale options
    YES_NO = [('Yes', 'Yes'),
              ('No', 'No')]

    # Color choices
    COLOR_CHOICES = [('Red', 'Red'),
                     ('Green', 'Green'),
                     ('Blue', 'Blue'),
                     ('Magenta', 'Magenta'),
                     ('Purple', 'Purple'),
                     ('Orange', 'Orange'),
                     ('Yellow', 'Yellow'),
                     ('Brown', 'Brown'),
                     ('Black', 'Black')]

    # Count options for Individual Statistic
    COUNT_OPTIONS = [('Total Count', 'Total Count'),
                     ('Daily average', 'Daily average'),
                     ('Monthly average', 'Monthly average'),
                     ('Yearly average', 'Yearly average')]

    GRAPH_CHOICES = [('Bar Graph', 'Bar Graph'),
                     ('Histogram', 'Histogram'),
                     ('Line Graph', 'Line Graph'),
                     ('Pie Chart', 'Pie Chart'),
                     ('Scatter Plot', 'Scatter Plot'),
                     ('Individual Statistic', 'Individual Statistic')]

    # Percentages, count, or both
    PIE_DATA_OPTIONS = [('Percent of total', 'Percent of total'),
                        ('Count', 'Count'),
                        ('Both percentages and count', 'Both percentages and count')]

    COUNT_OPTIONS = [('Total Count', 'Total Count'),
                     ('Daily average', 'Daily average'),
                     ('Monthly average', 'Monthly average'),
                     ('Yearly average', 'Yearly average')]

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

    HIST_TIME_CHOICES = [('Time of Day', 'Time of Day'),
                         ('Months', 'Months'),
                         ('Years', 'Years')]

    LINE_DISP_CHOICES = [('Dots', 'Dots'),
                         ('Lines', 'Lines'),
                         ('Dots and Lines', 'Dots and Lines')]

    GPA_COMPARISON = [('Average end term Semester GPA', 'Average end term Semester GPA'),
                      ('Average end term Cumulative GPA', 'Average end term Cumulative GPA'),
                      ('Average end term Attempted Credits', 'Average end term Attempted Credits'),
                      ('Average end term Earned Credits', 'Average end term Earned Credits'),
                      (
                      'Average end term Cumulative Completed Credits', 'Average end term Cumulative Completed Credits')]

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

    TIME_VS_COMPARISONS = [('Count visits over time', 'Count visits over time'),
                           ('Compare GPA against demographics', 'Compare GPA against demographics')]

    # Required for all report types
    graph_type = models.CharField(max_length=50)
    title = models.CharField(choices=YES_NO, max_length=20)

    # Required for Bar Graphs and Individual Statistics
    report_type = models.CharField(choices=TIME_VS_COMPARISONS, null=True, max_length=120)
    category = models.CharField(choices=DEMO, null=True, max_length=120)
    gpa_to_compare = models.CharField(choices=GPA_COMPARISON, null=True, max_length=120)

    # Required for all report types except Histogram
    selection = models.CharField(choices=DEMOGRAPHICS, max_length=50, null=True)

    # Required for Bar Graph only
    multiple_bars = models.CharField(choices=YES_NO, max_length=20, null=True)

    # Required for Histogram only
    time_units = models.CharField(choices=HIST_TIME_CHOICES, null=True, max_length=50)

    # Required for everything except Individual Statistic
    locations = models.CharField(max_length=500, null=True)
    select_all = models.BooleanField(null=True)
    include_table = models.CharField(choices=YES_NO, max_length=50, null=True)
    use_custom_event_name = models.CharField(choices=YES_NO, null=True, max_length=50)
    custom_event_name = models.CharField(max_length=100, null=True)

    # Required for Bar Graph and Histogram
    select_bar_color = models.CharField(choices=COLOR_CHOICES, max_length=50, null=True)

    # Required for everything except Individual Statistic and Pie Chart
    autoscale = models.CharField(choices=YES_NO, max_length=50, null=True)
    max_count = models.IntegerField(null=True)
    increment_by = models.IntegerField(null=True)

    # Required for Histogram only
    hist_data = models.CharField(max_length=50, null=True)

    # Required for Line Graph only
    dot_color = models.CharField(choices=COLOR_CHOICES, max_length=50, null=True)
    display_options = models.CharField(choices=LINE_DISP_CHOICES, max_length=50, null=True)

    # Required for Pie Chart only
    data_units = models.CharField(choices=PIE_DATA_OPTIONS, max_length=50, null=True)

    # Required for scatter plot only
    dot_color = models.CharField(choices=COLOR_CHOICES, max_length=50, null=True)


    # Required for Individual Statistic only
    count_options = models.CharField(choices=COUNT_OPTIONS, max_length=50, null=True)
    header_font_color = models.CharField(choices=COLOR_CHOICES, max_length=50, null=True)
    statistic_font_color = models.CharField(choices=COLOR_CHOICES, max_length=50, null=True)
    header_font_size = models.IntegerField(choices=FONT_CHOICES, null=True)
    statistic_font_size = models.IntegerField(choices=FONT_CHOICES, null=True)

    preset_name = models.CharField(max_length=100, primary_key=True)

    # Each graph preset is linked to a user (many-to-one relationship)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, max_length=50, null=True)
