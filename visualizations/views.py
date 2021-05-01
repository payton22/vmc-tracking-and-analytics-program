import os

from django.http import HttpResponse
from django.shortcuts import render
from plotly.offline import plot
from plotly.graph_objs import Bar
from plotly.graph_objs import Figure
from plotly.graph_objs import Layout
import random
from pages import views as pageViews
from visualizations.models import ReportPresets
from datetime import datetime
from pages.views import TimeFrame
from django.views.static import serve
from urllib.parse import unquote
import sqlite3

import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objects as go

from django_plotly_dash import DjangoDash

import csv

import os;

# Path for getting the Python scripts for database queries
print(os.path.dirname(__file__))
# Subdirectory labeled "sql_queries"
for module in os.listdir(os.path.dirname(__file__) + '/sql_queries'):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    # Import the sql query script
    exec('from .sql_queries import ' + module[:-3] + ' as ' + module[:-3]);
del module;


# Exception thrown for empty queries
# Should not reach this point
class emptyList(Exception):
    pass


# ReportGenerator base class
# Used in conjunction with the State design pattern
class ReportGenerator():
    def __init__(self, request, data):
        # HTTP request
        self.request = request
        # Data that contains the wizard form submission
        self.data = data
        # Default is BarGraph
        self.barGraph = BarGraph(self, self.request, self.data)

        # Default state = bar graph
        self.state = self.barGraph
        # Get the current state
        self.state.findState()

    # Setters ------------
    def setState(self, state):
        self.state = state

    def setData(self, data):
        self.data = data

    # End of setters -------

    # Function that is common between all graph types
    # Get the report, return the Dash widget
    def generateReport(self):
        app, title, validDates = self.state.generateReport()
        return app, title, validDates


# State design pattern
class State:

    def __init__(self, reportGenerator, request, data):
        self.reportGenerator = reportGenerator
        self.request = request
        self.data = data

    # Abstract state methods
    def findState(self):
        pass

    def generateReport(self):
        pass

    def checkDates(self):
        pass

    def checkIfPreset(self):
        pass

    def checkGraphType(self, data):
        pass

    # If the user specifies that they want to use a custom title on the first page of the Reports Wizard,
    # get the custom title here
    def get_custom_title(self):
        form_dict = self.data['form_data']
        inner_dict = form_dict[0]
        custom_title = inner_dict['title']

        return custom_title

    # Check if any visits were returned based on the user's query. If visits
    # were returned, return False
    def checkInvalidQuery(self, results):
        if not results:
            return False
        else:
            return True


# BarGraph (inherts from State)
class BarGraph(State):
    def __init__(self, reportGenerator, request, data):
        super(BarGraph, self).__init__(reportGenerator, request, data)

    # BarGraph is the default state, but we need to check if the user wants a different type of report
    # e.g. if the user wants a Histogram, enter the histogram state
    def findState(self):
        # Wizard form data is based on a nested dictionary structure
        # Eeach of the wizard form fields represent a key to the dictionary

        inner_dict = self.data['form_data']
        graph_type = inner_dict[0]

        if graph_type['graphType'] == 'Bar Graph':
            self.reportGenerator.setState(self)
        elif graph_type['graphType'] == 'Histogram':
            self.reportGenerator.setState(Histogram(self.reportGenerator, self.request, self.data))
        elif graph_type['graphType'] == 'Pie Chart':
            self.reportGenerator.setState(PieChart(self.reportGenerator, self.request, self.data))
        elif graph_type['graphType'] == 'Line and/or Scatter':
            self.reportGenerator.setState(ScatterPlot(self.reportGenerator, self.request, self.data))
        elif graph_type['graphType'] == 'Individual Statistic':
            self.reportGenerator.setState(IndividualStatistic(self.reportGenerator, self.request, self.data))

    # Check the graph type from the wizard, make corresponding variable conversions
    # for SQL querying
    def determineSelection(self):
        # Pull from the wizard form data
        self.inner_dict = self.data['form_data']
        self.selection_dict = self.inner_dict[1]
        self.selection = self.selection_dict['selection']

        self.include_table = self.selection_dict['include_table']
        self.report_type = self.selection_dict['report_type']
        self.category = self.selection_dict['category']
        self.gpa_to_compare = self.selection_dict['gpa_to_compare']

        if self.report_type == 'Count visits over time':
            self.title = self.selection
        elif self.report_type == 'Compare GPA against demographics':
            self.title = self.category

        # Convert selection into query '*' for SQL
        # This will be used to gather the appropriate python query script from the "sql_queries" subdirectory
        # Each key represents a choice in the Wizard
        # Each key will then correspond to the python script that will run the query
        # E.g. "end_term_term_gpa" = "end_term_term_gpa.py"
        self.query_dictionary = {'End Term Semester GPA': 'end_term_term_gpa',
                                 'End Term Cumulative GPA': 'end_term_cumulative_gpa',
                                 'End Term Attempted Credits': 'end_term_attempted_credits', 'End Term Earned Credits':
                                     'end_term_earned_credits',
                                 'End Term Cumulative Completed Credits': 'end_term_credit_completion',
                                 'Benefit Chapter': 'benefit_chapter',
                                 'Residential Distance from Campus': 'currently_live', 'Employment': 'employment',
                                 'Weekly Hours Worked': 'work_hours', 'Number of Dependents': 'dependents',
                                 'Marital Status': 'marital_status', 'Gender Identity': 'gender',
                                 'Parent Education': 'parent_education', 'STEM Major': 'is_stem',
                                 'Pell Grant': 'pell_grant', 'Needs Based Grants/Scholarships': 'needs_based',
                                 'Merits Based Grants/Scholarships': 'merit_based',
                                 'Federal Work Study': 'federal_work_study', 'Military Grants': 'military_grants',
                                 'Millennium Scholarship': 'millennium_scholarship',
                                 'Nevada Pre-Paid': 'nevada_prepaid',
                                 'Best Method of Contact': 'contact_method',
                                 'Break in University Attendance': 'break_in_attendance',
                                 'Total Usage by Location': 'total_usage_by_location', 'GPA': 'gpa',
                                 'Usage by Date': 'usage_by_date', 'Classification': 'classification', 'Major': 'major',
                                 'Services': 'services'}

        # If the user wants a GPA vs. demographics report, this dictionary will be used to
        # gather the approrpiate python script from the "sql_queries" subdirectory
        self.gpa_dictionary = {'Average end term Semester GPA': 'end_term_term_gpa',
                               'Average end term Cumulative GPA': 'end_term_cumulative_gpa',
                               'Average end term Attempted Credits': 'end_term_attempted_credits',
                               'Average end term Earned Credits': 'end_term_earned_credits',
                               'Average end term Cumulative Completed Credits': 'end_term_credit_completion'}
        # self.conn_string_sql = eval(self.query_dictionary[self.selection] + '.get_query()');

    # Get the date range for database querying
    def determineDateRange(self):
        self.date_subdict = self.inner_dict[2]
        self.from_time = self.date_subdict['from_time']
        self.to_time = self.date_subdict['to_time']

    # Styling page from the Reports Wizard
    # Common to all graph types, but the specifics vary based on the graph selection
    def determineStyleSettings(self):
        self.style_dict = self.inner_dict[3]
        self.bar_color = self.style_dict['select_bar_color']
        self.autoscale = self.style_dict['autoscale']
        if self.autoscale == 'No':
            self.max_count = self.style_dict['max_count']
            self.increment_by = self.style_dict['increment_by']
        self.show_multiple_bars = self.style_dict['show_multiple_bars_by_location']

    # Get the locations that the user want to track visits for
    # Ex: user will enter "VS Fitzgerald" and "VS Event"
    # This will get "VS Fitzgerald" and "VS Event" checkbox selections and store them for the query
    def determineLocationsToTrack(self):
        self.location_dict = self.inner_dict[4]
        self.location_list = self.location_dict['attendance_data']
        self.select_all = self.location_dict['select_all']
        self.use_custom_event_name = self.location_dict['use_custom_event_name']
        self.custom_event_name = self.location_dict['custom_event_name']
        # Check if the user wants to select all locations to represent this choice in the report
        # title (if not custom title)
        if self.select_all:
            self.all_locations = True
        else:
            self.all_locations = False

    # The main function that will generate the report
    def generateReport(self):
        # Get all of the user's choices from the Reports Wizard
        self.determineSelection()
        self.determineDateRange()
        self.determineStyleSettings()
        self.determineLocationsToTrack()

        # If the user wants to include all locations that they selected into a single bar for each category
        if self.show_multiple_bars == 'No':
            app, title, validDates = self.generateSingleBars()
            return app, title, validDates
        # If the user wants to separate the bars for each category based on location
        elif self.show_multiple_bars == 'Yes':
            app, title, validDates = self.generateGroupedBars()
            return app, title, validDates

    def generateSingleBars(self):
        # Connect to the database
        conn = sqlite3.connect('vmc_tap.db');
        conn_results = []

        # Determines the default title
        # Either visits based report, or GPA-based demographics report
        if self.all_locations:
            if self.report_type == 'Count visits over time':
                self.title = "Count of " + self.title + ", all Locations from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
            elif self.report_type == 'Compare GPA against demographics':
                self.title = self.gpa_to_compare + " by " + self.category + ", all Locations, from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
        # If the user did not select all available locations, include each location selection in the title rather than
        # "all locations"
        else:
            loc_str = ''
            for loc in self.location_list:
                if loc != self.location_list[-1]:
                    loc_str += loc + ', '
                else:
                    loc_str += loc
            # Generates a non-custom title (if custom title was not selected) for individual locations,
            # if the user did not select "all locations"
            if self.report_type == 'Count visits over time':
                self.title = "Count of " + self.title + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
            elif self.report_type == 'Compare GPA against demographics':
                self.title = self.gpa_to_compare + " by " + self.category + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')

        # If the user opted for a custom title, get the name of the custom title
        custom_title = self.get_custom_title()
        if custom_title == '':
            title = self.title
        else:
            title = custom_title

        substr = "\""
        # Gather the user's location selections from the Reports Wizard to put them in the correct format
        # for the SQL query
        for i, location in enumerate(self.location_list):
            if i != (len(self.location_list) - 1):
                substr += location + '\' or location = \''
            else:
                substr += location

        substr += '"'

        # If the user wants to query visits over a given date range,
        # get the appropriate python script for the query, passing in the date range and locations
        # Each python script has a single function called "get_query()" but the details of the function
        # vary based on the type of query
        if self.report_type == 'Count visits over time':
            self.conn_string_sql = eval(
                self.query_dictionary[self.selection] + ".get_query('" + self.from_time.strftime(
                    '%Y-%m-%d') + "', '" + self.to_time.strftime(
                    '%Y-%m-%d') + "', " + substr + ")")
        # Same as above, except the user is querying GPA vs. demographics instead of visits
        elif self.report_type == 'Compare GPA against demographics':
            self.conn_string_sql = eval(
                self.query_dictionary[self.category] + "_gpa.get_query('" + self.gpa_dictionary[
                    self.gpa_to_compare] + "', '" + self.from_time.strftime(

                    '%Y-%m-%d') + "', '" + self.to_time.strftime(
                    '%Y-%m-%d') + "', " + substr + ")")

        # Execute the database query via the SQL command obtained
        for d in conn.execute(self.conn_string_sql):
            conn_results.append(d);

        conn.close()

        # Rotates 2D array to work w/ plotly
        conn_results_rotated = list(zip(*conn_results[::-1]))

        # If the query returned valid visits
        if conn_results_rotated:
            # If the user used a custom event name
            if 'Veteran Services Event' in conn_results_rotated[0] and self.use_custom_event_name == 'Yes':
                # Replace all results returned in the query that state "Veteran Services Event" to the
                # name of the custom event specified by the user
                conn_results_rotated[0] = list(conn_results_rotated[0])
                i = conn_results_rotated[0].index('Veteran Services Event')
                custom_name = self.custom_event_name
                conn_results_rotated[0][i] = custom_name
                conn_results_rotated[0] = tuple(conn_results_rotated[0])

        app = DjangoDash('Graph')  # replaces dash.Dash

        # Check if the query was valid
        validDates = self.checkInvalidQuery(conn_results_rotated)

        # If the query did not return any visits, fill the x and y axis with placeholders
        if not validDates:
            x_axis = [1, 2, 3, 4, 5, 6, 7, 8]
            y_axis = [1, 2, 3, 4, 5, 6, 7, 8]
        else:
            # Extract the x and y-axis from the tuple results
            x_axis = conn_results_rotated[0]
            y_axis = conn_results_rotated[1]
            # Convert the tuples into Python lists
            x_axis = x_axis[::-1]
            y_axis = y_axis[::-1]

        # If autoscaling is not enabled by the user, we need to set the max count of the y-axis
        if self.autoscale != 'Yes':
            layout = go.Layout(title=title, yaxis=dict(range=[0, self.max_count]))
        else:
            layout = Layout(title=title)

        # Setup the bar graph object to display via Plotly/Dash
        fig = go.Figure(data=[go.Bar(x=x_axis, y=y_axis, marker=dict(color=self.bar_color.lower()))], layout=layout)
        fig.update_xaxes(type='category')

        # Now implement the custom scaling if enabled
        if self.autoscale != 'Yes':
            fig.update_yaxes(dtick=self.increment_by)

        # Dash instance for including a table
        if self.include_table == 'Yes' and validDates:
            header = ['Row Labels', 'Count of Location']
            x_list = list(x_axis)
            y_list = list(y_axis)

            # If we are counting visits over time, get the grand total
            if self.report_type == 'Count visits over time':
                total = 0
                for count in y_axis:
                    total += count

                x_list.append('<b>Grand Total</b>')
                y_list.append(total)
            # If we are getting averages, get the average instead of a grand total
            elif self.report_type == 'Compare GPA against demographics':
                total_values = len(y_list)
                total = 0
                for count in y_axis:
                    total += count
                x_list.append('<b>Total Average<b>')
                total /= total_values
                y_list.append(round(total, 2))

            # Convert table values into list format as required by Plotly
            values = [x_list, y_list]

            # Setup the table object to be rendered later by Dash/Plotly
            table = go.Figure(
                data=[go.Table(header=dict(values=header, align='left'), cells=dict(values=values, align='left'))],
                layout=Layout(title=title))
            table.update_layout(height=(220 + len(x_list) * 25))

            # Create a separate list to setup the CSV file
            new_x_list = []

            # Go though the table list and get rid of the '<b>' HTML markers -- not wanted for a CSV file
            for i, stri in enumerate(x_list):
                if isinstance(stri, int) or isinstance(stri, float):
                    replaced_str = str(stri)
                    x_list[i] = replaced_str
                    stri = replaced_str
                temp_new_string = stri.replace('<b>', '')
                new_string = temp_new_string.replace('</b>', '')
                new_x_list.append(new_string)

            # Setup the new list for the CSV file
            values = [new_x_list, y_list]

            # Generate the CSV file
            genTableFile(header, values)

            # Dash layout if the table is included
            app.layout = html.Div(children=[dcc.Graph(id='table', figure=table)
                , dcc.Graph(id='figure', figure=fig, style={'height': '40vh'}),
                                            ], style={'height': '40vh', 'width': '70vw'})
        else:
            # Dash layout if the table is not included
            app.layout = html.Div(children=[
                dcc.Graph(id='figure', figure=fig, style={'height': '90vh'}),
            ], style={'height': '70vh', 'width': '70vw'})

        return app, title, validDates

    def generateGroupedBars(self):

        # Connect to the database
        conn = sqlite3.connect('vmc_tap.db');
        conn_results = []

        # Determines the default title
        # Either visits based report, or GPA-based demographics report
        if self.all_locations:
            if self.report_type == 'Count visits over time':
                self.title = "Count of " + self.title + ", all Locations from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
            elif self.report_type == 'Compare GPA against demographics':
                self.title = self.gpa_to_compare + " by " + self.category + ", all Locations, from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')

        # If the user did not select all available locations, include each location selection in the title rather than
        # "all locations"
        else:
            loc_str = ''
            for loc in self.location_list:
                if loc != self.location_list[-1]:
                    loc_str += loc + ', '
                else:
                    loc_str += loc

            # Generates a non-custom title (if custom title was not selected) for individual locations,
            # if the user did not select "all locations"
            if self.report_type == 'Count visits over time':
                self.title = "Count of " + self.title + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
            elif self.report_type == 'Compare GPA against demographics':
                self.title = self.gpa_to_compare + " by " + self.category + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')

        # If the user opted for a custom title, get the name of the custom title
        custom_title = self.get_custom_title()
        if custom_title == '':
            title = self.title
        else:
            title = custom_title

        substr = ''

        for i, location in enumerate(self.location_list):
            if i != (len(self.location_list) - 1):
                substr += location + '\' or location = \''
            else:
                substr += location

        self.conn_string_sql = []

        # If the user wants to query visits over a given date range,
        # get the appropriate python script for the query, passing in the date range and locations
        # Each python script has a single function called "get_query()" but the details of the function
        # vary based on the type of query
        if self.report_type == 'Count visits over time':
            for location in self.location_list:
                loc_str = "'"
                loc_str += location + "'"
                self.conn_string_sql.append(
                    eval(self.query_dictionary[self.selection] + ".get_query('" + self.from_time.strftime(
                        '%Y-%m-%d') + "', '" + self.to_time.strftime(
                        '%Y-%m-%d') + "', " + loc_str + ")"))
        # Same as above, except the user is querying GPA vs. demographics instead of visits
        elif self.report_type == 'Compare GPA against demographics':
            for location in self.location_list:
                loc_str = "'"
                loc_str += location + "'"
                self.conn_string_sql.append(eval(
                    self.query_dictionary[self.category] + "_gpa.get_query('" + self.gpa_dictionary[
                        self.gpa_to_compare] + "', '" + self.from_time.strftime(

                        '%Y-%m-%d') + "', '" + self.to_time.strftime(
                        '%Y-%m-%d') + "', " + loc_str + ")"))

        location_results = []
        valid_dates = []

        for i, location in enumerate(self.location_list):
            conn_results = []
            for d in conn.execute(self.conn_string_sql[i]):
                conn_results.append(d)
            # Rotates 2D array to work w/ plotly
            conn_results_rotated = list(zip(*conn_results[::-1]))

            # If the query returned valid visits
            if conn_results_rotated:
                # If the user used a custom event name
                if 'Veteran Services Event' in conn_results_rotated[0] and self.use_custom_event_name == 'Yes':
                    # Replace all results returned in the query that state "Veteran Services Event" to the
                    # name of the custom event specified by the user
                    conn_results_rotated[0] = list(conn_results_rotated[0])
                    i = conn_results_rotated[0].index('Veteran Services Event')
                    custom_name = self.custom_event_name
                    conn_results_rotated[0][i] = custom_name
                    conn_results_rotated[0] = tuple(conn_results_rotated[0])
                location_results.append(conn_results_rotated)
            valid_dates.append(self.checkInvalidQuery(conn_results_rotated))

        conn.close()

        app = DjangoDash('Graph')  # replaces dash.Dash

        y_axis = []
        x_axis = []
        validDates = True
        # If the query did not return any visits, fill the x and y axis with placeholders
        for i, location in enumerate(self.location_list):
            if not valid_dates[i]:
                validDates = False
                x_axis.append([1, 2, 3, 4, 5, 6, 7, 8])
                y_axis.append([1, 2, 3, 4, 5, 6, 7, 8])
            else:
                # Extract the x and y-axis from the tuple results
                x_results = location_results[i][0]
                y_results = location_results[i][1]
                x_results = x_results[::-1]
                y_results = y_results[::-1]
                x_axis.append(x_results)
                y_axis.append(y_results)

        # If autoscaling is not enabled by the user, we need to set the max count of the y-axis
        if self.autoscale != 'Yes':
            layout = go.Layout(title=title, yaxis=dict(range=[0, self.max_count]))
        else:
            layout = Layout(title=title)

        data_list = []
        for i, location in enumerate(self.location_list):
            if location == 'Veteran Services Event' and self.use_custom_event_name == 'Yes':
                data_list.append(go.Bar(name=self.custom_event_name, x=x_axis[i], y=y_axis[i]))
            else:
                data_list.append(go.Bar(name=location, x=x_axis[i], y=y_axis[i]))

        fig = go.Figure(data=data_list, layout=layout)
        # Now implement the custom scaling if enabled
        if self.autoscale != 'Yes':
            fig.update_yaxes(dtick=self.increment_by)


        # Dash instance for includng a table
        if self.include_table == 'Yes':
            header = ['Row Labels', 'Count of Location']
            x_list = []
            y_list = []

            # Append the inner list for each location
            for i, location in enumerate(self.location_list):
                x_list.append(list(x_axis[i]))
                y_list.append(list(y_axis[i]))


            running_total = 0
            print('x_list', x_list)
            print('y_list', y_list)
            for i, location in enumerate(self.location_list):
                # If we are counting visits over time, get the grand total
                if self.report_type == 'Count visits over time':
                    x_list[i].insert(0, '<b>Location<b>')
                    y_list[i].insert(0, '<b>' + location + '<b>')
                    loc_subtotal = 0
                    for count in y_list[i]:
                        if isinstance(count, int) or isinstance(count, float):
                            loc_subtotal += count

                    x_list[i].append('<b>Total for location<b>')
                    y_list[i].append(loc_subtotal)
                    running_total += loc_subtotal
                # If we are getting averages, get the average instead of a grand tota
                elif self.report_type == 'Compare GPA against demographics':
                    total_values = len(y_list[i])
                    x_list[i].insert(0, '<b>Location<b>')
                    y_list[i].insert(0, '<b>' + location + '<b>')
                    loc_subtotal = 0
                    for count in y_list[i]:
                        if isinstance(count, int) or isinstance(count, float):
                            loc_subtotal += count

                    x_list[i].append('<b>Total Average for location<b>')
                    loc_subtotal /= total_values
                    y_list[i].append(round(loc_subtotal, 2))
                    running_total += loc_subtotal

            # --- Referenced from Stack Overflow https://stackabuse.com/python-how-to-flatten-list-of-lists/
            # Last visited 3/6/2021
            flattened_x_list = [value for loc in x_list for value in loc]

            if conn_results_rotated:
                if conn_results_rotated[0]:
                    if 'Veteran Services Event' in conn_results_rotated[0] and self.use_custom_event_name == 'Yes':
                        i = flattened_x_list.index('Veteran Services Event')
                        flattened_x_list[i] = self.custom_event_name

            flattened_y_list = [value for loc in y_list for value in loc]
            # End of reference -----------------------------------------------------------------------------

            flattened_x_list.append('<b>Grand Total</b>')

            if self.report_type == 'Compare GPA against demographics':
                running_total /= len(self.location_list)

            # Round the average to 2 decimal places
            flattened_y_list.append(round(running_total, 2))

            values = [flattened_x_list, flattened_y_list]

            # Dash layout if the table is included
            table = go.Figure(
                data=[go.Table(header=dict(values=header, align='left'), cells=dict(values=values, align='left'))],
                layout=Layout(title=title))
            table.update_layout(height=(220 + len(flattened_x_list) * 25))

            # Setup the new list for the CSV file
            new_x_list = []

            # Get rid of the <b> HTML markers that were used in the table
            for value in flattened_x_list:
                if isinstance(value, str):
                    temp_new_string = value.replace('<b>', '')
                    new_string = temp_new_string.replace('</b>', '')
                    new_x_list.append(new_string)

            # Repeat te process for the y-axis, getting rid of the HTML <b> markers
            new_y_list = []
            for value in flattened_y_list:
                if isinstance(value, str):
                    temp_new_string = value.replace('<b>', '')
                    new_string = temp_new_string.replace('</b>', '')
                    new_y_list.append(new_string)
                else:
                    new_y_list.append(value)

            # Generate the CSV file
            values = [new_x_list, new_y_list]

            genTableFile(header, values)

            # Dash layout if table is included
            app.layout = html.Div(children=[dcc.Graph(id='table', figure=table)
                , dcc.Graph(id='figure', figure=fig, style={'height': '40vh'}),
                                            ], style={'height': '40vh', 'width': '70vw'})

        # Dash layout without the table
        else:
            app.layout = html.Div(children=[
                dcc.Graph(id='figure', figure=fig, style={'height': '90vh'}),
            ], style={'height': '70vh', 'width': '70vw'})

        return app, title, validDates

# Histogram (inherits from State)
# Returns a Plotly/Dash Histogram to the user for reporting purposes
class Histogram(State):
    def __init__(self, reportGenerator, request, data):
        super(Histogram, self).__init__(reportGenerator, request, data)

    # Get the current state from the State design pattern structure
    def findState(self):
        # Wizard form data is based on a nested dictionary structure
        # Each of the wizard form fields represent a key to the dictionary
        inner_dict = self.data['form_data']
        graph_type = inner_dict[0]

        if graph_type['graphType'] == 'Bar Graph':
            self.reportGenerator.setState(self)
        elif graph_type['graphType'] == 'Pie Chart':
            self.reportGenerator.setState(PieChart(self.reportGenerator, self.request, self.data))
        elif graph_type['graphType'] == 'Line and/or Scatter':
            self.reportGenerator.setState(ScatterPlot(self.reportGenerator, self.request, self.data))
        elif graph_type['graphType'] == 'Individual Statistic':
            self.reportGenerator.setState(IndividualStatistic(self.reportGenerator, self.request, self.data))

    # Check the graph type from the wizard, make corresponding variable conversions
    # for SQL querying
    def determineSelection(self):
        # Pull from the wizard form data
        self.inner_dict = self.data['form_data']
        self.selection_dict = self.inner_dict[1]
        self.selection = self.selection_dict['time_units']
        self.title = self.selection
        self.include_table = self.selection_dict['include_table']

        # This will be used to gather the appropriate python query script from the "sql_queries" subdirectory
        # Each key represents a choice in the Wizard
        # Each key will then correspond to the python script that will run the query
        # E.g. "end_term_term_gpa" = "end_term_term_gpa.py"
        self.query_dictionary = {'Average visitors by time': 'avg_by_time', 'Average visitors by day': 'avg_by_day',
                                 'Total visitors by day': 'total_by_day', 'Total visitors by year': 'total_by_year'}

    # Get the date range for database querying
    def determineDateRange(self):
        self.date_subdict = self.inner_dict[2]
        self.from_time = self.date_subdict['from_time']
        self.to_time = self.date_subdict['to_time']

    # Styling page from the Reports Wizard
    # Common to all graph types, but the specifics vary based on the graph selection
    def determineStyleSettings(self):
        self.style_dict = self.inner_dict[3]
        self.bar_color = self.style_dict['select_bar_color']
        self.autoscale = self.style_dict['autoscale']
        if self.autoscale == 'No':
            self.max_count = self.style_dict['max_count']
            self.increment_by = self.style_dict['increment_by']

    # Get the locations that the user want to track visits for
    # Ex: user will enter "VS Fitzgerald" and "VS Event"
    # This will get "VS Fitzgerald" and "VS Event" checkbox selections and store them for the query
    def determineLocationsToTrack(self):
        self.location_dict = self.inner_dict[4]
        self.location_list = self.location_dict['attendance_data']
        self.select_all = self.location_dict['select_all']
        if self.select_all:
            self.all_locations = True
        else:
            self.all_locations = False

    # The main function that will generate the report
    def generateReport(self):
        self.determineSelection()
        self.determineDateRange()
        self.determineStyleSettings()
        self.determineLocationsToTrack()

        conn = sqlite3.connect('vmc_tap.db');
        conn_results = []

        # If the user wants to include all locations that they selected into a single bar for each category
        if self.all_locations:
            self.title = "Count of " + self.title + ", All Locations, from " + self.from_time.strftime(
                '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
        # If the user wants to separate the bars for each category based on location
        else:
            loc_str = ''
            for loc in self.location_list:
                if loc != self.location_list[-1]:
                    loc_str += loc + ', '
                else:
                    loc_str += loc

            # Determines the default title
            # Based on date range and selected locations
            self.title = "Count of " + self.title + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')

        # Get the custom title from the form (if selected by the user)
        custom_title = self.get_custom_title()
        if custom_title == '':
            title = self.title
        else:
            title = custom_title

        substr = "\""

        # Gather the user's location selections from the Reports Wizard to put them in the correct format
        # for the SQL query
        for i, location in enumerate(self.location_list):
            if i != (len(self.location_list) - 1):
                substr += location + '\' or location = \''
            else:
                substr += location

        substr += '"'

        # If the user wants to query visits over a given date range,
        # get the appropriate python script for the query, passing in the date range and locations
        # Each python script has a single function called "get_query()" but the details of the function
        # vary based on the type of query
        self.conn_string_sql = eval(self.query_dictionary[self.selection] + ".get_query('" + self.from_time.strftime(
            '%Y-%m-%d') + "', '" + self.to_time.strftime(
            '%Y-%m-%d') + "', " + substr + ")")

        # Execute the database query via the SQL command obtained
        for d in conn.execute(self.conn_string_sql):
            conn_results.append(d);

        conn.close()

        # Rotates 2D array to work w/ plotly
        conn_results_rotated = list(zip(*conn_results[::-1]));

        app = DjangoDash('Graph')  # replaces dash.Dash

        # Check if the query was valid
        validDates = self.checkInvalidQuery(conn_results_rotated)

        # If the query did not return any visits, fill the x and y axis with placeholders
        if not validDates:
            x_axis = [1, 2, 3, 4, 5, 6, 7, 8]
            y_axis = [1, 2, 3, 4, 5, 6, 7, 8]
        # Extract the x and y-axis from the tuple results
        else:
            x_axis = conn_results_rotated[0]
            x_axis = x_axis[::-1]
            x_axis = list(x_axis)

            y_axis = conn_results_rotated[1]
            y_axis = y_axis[::-1]
            y_axis = list(y_axis)

        # If autoscaling is not enabled by the user, we need to set the max count of the y-axis
        if self.autoscale != 'Yes':
            layout = go.Layout(title=title, yaxis=dict(range=[0, self.max_count]))
        else:
            layout = Layout(title=title)

        # Setup the Histogram object to display based on the user's settings from the Wizard
        fig = go.Figure(layout=layout)
        fig.add_trace(
            go.Histogram(histfunc="sum", y=y_axis, x=x_axis, name="count", marker=dict(color=self.bar_color.lower())))
        fig.update_layout(bargap=0)

        if self.selection == 'Total visitors by year':
            fig.update_xaxes(type='category')
        # fig.update_layout(bargap=0)

        # Now implement the custom scaling if enabled
        if self.autoscale != 'Yes':
            fig.update_yaxes(dtick=self.increment_by)

        # Dash instance for including a table
        if self.include_table == 'Yes' and validDates:
            header = ['Row Labels', 'Count of Location']
            x_list = list(x_axis)
            y_list = list(y_axis)
            values = [x_list, y_list]
            print('values: ', values)

            total = 0
            for count in y_axis:
                total += count

            # Get the grand total for the total count in the table
            x_list.append('<b>Grand Total</b>')
            y_list.append(total)

            # Setup the table object for display
            table = go.Figure(
                data=[go.Table(header=dict(values=header, align='left'), cells=dict(values=values, align='left'))],
                layout=Layout(title=title))
            table.update_layout(height=(220 + len(x_list) * 23))

            # Start a new list for the CSV file based on the x-axis
            new_x_list = []

            # Get rid of the HTML <b> markers (not needed in CSV)
            for str in x_list:
                temp_new_string = str.replace('<b>', '')
                new_string = temp_new_string.replace('</b>', '')
                new_x_list.append(new_string)

            # Construct the new list for the CSV file
            values = [new_x_list, y_list]

            # Generate the CSV file
            genTableFile(header, values)
            # Dash layout if table is included
            app.layout = html.Div(children=[dcc.Graph(id='table', figure=table)
                , dcc.Graph(id='figure', figure=fig, style={'height': '40vh'}),
                                            ], style={'height': '40vh', 'width': '70vw'})
        # Dash layout if table is not included
        else:
            app.layout = html.Div(children=[
                dcc.Graph(id='figure', figure=fig, style={'height': '90vh'}),
            ], style={'height': '70vh', 'width': '70vw'})

        return app, title, validDates

# PieChart (inherits from State)
class PieChart(State):
    def __init__(self, reportGenerator, request, data):
        super(PieChart, self).__init__(reportGenerator, request, data)

    # Get the current state based on the user's choice in the Reports Wizard
    def findState(self):
        inner_dict = self.data['form_data']
        graph_type = inner_dict[0]

        if graph_type['graphType'] == 'Pie Chart':
            self.reportGenerator.setState(self)

    # Check the graph type from the wizard, make corresponding variable conversions
    # for SQL querying
    def determineSelection(self):
        # Pull from the wizard form data
        self.inner_dict = self.data['form_data']
        self.selection_dict = self.inner_dict[1]
        self.selection = self.selection_dict['selection']
        self.title = self.selection
        self.include_table = self.selection_dict['include_table']

        # Convert selection into query '*' for SQL
        # This will be used to gather the appropriate python query script from the "sql_queries" subdirectory
        # Each key represents a choice in the Wizard
        # Each key will then correspond to the python script that will run the query
        # E.g. "end_term_term_gpa" = "end_term_term_gpa.py"
        self.query_dictionary = {'End Term Semester GPA': 'end_term_term_gpa',
                                 'End Term Cumulative GPA': 'end_term_cumulative_gpa',
                                 'End Term Attempted Credits': 'end_term_attempted_credits', 'End Term Earned Credits':
                                     'end_term_earned_credits',
                                 'End Term Cumulative Completed Credits': 'end_term_credit_completion',
                                 'Benefit Chapter': 'benefit_chapter',
                                 'Residential Distance from Campus': 'currently_live', 'Employment': 'employment',
                                 'Weekly Hours Worked': 'work_hours', 'Number of Dependents': 'dependents',
                                 'Marital Status': 'marital_status', 'Gender Identity': 'gender',
                                 'Parent Education': 'parent_education',
                                 'STEM Major': 'is_stem',
                                 'Pell Grant': 'pell_grant', 'Needs Based Grants/Scholarships': 'needs_based',
                                 'Merits Based Grants/Scholarships': 'merit_based',
                                 'Federal Work Study': 'federal_work_study', 'Military Grants': 'military_grants',
                                 'Millennium Scholarship': 'millennium_scholarship',
                                 'Nevada Pre-Paid': 'nevada_prepaid',
                                 'Best Method of Contact': 'contact_method',
                                 'Break in University Attendance': 'break_in_attendance',
                                 'Total Usage by Location': 'total_usage_by_location', 'GPA': 'gpa',
                                 'Usage by Date': 'usage_by_date', 'Classification': 'classification', 'Major': 'major',
                                 'Services': 'services'}

    # Get the date range for database querying
    def determineDateRange(self):
        self.date_subdict = self.inner_dict[2]
        self.from_time = self.date_subdict['from_time']
        self.to_time = self.date_subdict['to_time']

    # Styling page from the Reports Wizard
    # Common to all graph types, but the specifics vary based on the graph selection
    def determineStyleSettings(self):
        self.style_dict = self.inner_dict[3]
        self.style_selection = self.style_dict['Data_units']

        if self.style_selection == 'Both percentages and count':
            self.textinfo = 'value+percent'
        elif self.style_selection == 'Percent of total':
            self.textinfo = 'percent'
        elif self.style_selection == 'Count':
            self.textinfo = 'value'

    # Get the locations that the user want to track visits for
    # Ex: user will enter "VS Fitzgerald" and "VS Event"
    # This will get "VS Fitzgerald" and "VS Event" checkbox selections and store them for the query
    def determineLocationsToTrack(self):
        self.location_dict = self.inner_dict[4]
        self.location_list = self.location_dict['attendance_data']
        self.select_all = self.location_dict['select_all']
        self.use_custom_event_name = self.location_dict['use_custom_event_name']
        self.custom_event_name = self.location_dict['custom_event_name']

        if self.select_all:
            self.all_locations = True
        else:
            self.all_locations = False

    # The main function that will generate the report
    def generateReport(self):
        # Get all of the user's selections from the Reports Wizard
        self.determineSelection()
        self.determineDateRange()
        self.determineStyleSettings()
        self.determineLocationsToTrack()

        conn = sqlite3.connect('vmc_tap.db');
        conn_results = []

        # Determines the default title if the user selected all locations
        if self.all_locations:
            self.title = "Count of " + self.title + ", All Locations, from " + self.from_time.strftime(
                '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
        # Default title if the user did not select all locations
        else:
            # If the user did not select all available locations, include each location selection in the title rather than
            # "all locations"
            loc_str = ''
            for loc in self.location_list:
                if loc != self.location_list[-1]:
                    loc_str += loc + ', '
                else:
                    loc_str += loc

            # Generates a non-custom title (if custom title was not selected) for individual locations,
            # if the user did not select "all locations"
            self.title = "Count of " + self.title + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')

        # If the user opted for a custom title, get the name of the custom title
        custom_title = self.get_custom_title()
        if custom_title == '':
            title = self.title
        else:
            title = custom_title

        substr = "\""

        # Gather the user's location selections from the Reports Wizard to put them in the correct format
        # for the SQL query
        for i, location in enumerate(self.location_list):
            if i != (len(self.location_list) - 1):
                substr += location + '\' or location = \''
            else:
                substr += location

        substr += '"'

        # Build the SQL command for the database query based on the user's selections in the Reports Wizard
        # Each python script has a single function called "get_query()" but the details of the function
        # vary based on the type of query
        self.conn_string_sql = eval(self.query_dictionary[self.selection] + ".get_query('" + self.from_time.strftime(
            '%Y-%m-%d') + "', '" + self.to_time.strftime(
            '%Y-%m-%d') + "', " + substr + ")")

        for d in conn.execute(self.conn_string_sql):
            conn_results.append(d);

        conn.close()

        # Rotates 2D array to work w/ plotly
        conn_results_rotated = list(zip(*conn_results[::-1]));

        # If the query returned valid visits
        if conn_results_rotated:
            # If the user used a custom event name
            if 'Veteran Services Event' in conn_results_rotated[0] and self.use_custom_event_name == 'Yes':
                # Replace all results returned in the query that state "Veteran Services Event" to the
                # name of the custom event specified by the user
                conn_results_rotated[0] = list(conn_results_rotated[0])
                i = conn_results_rotated[0].index('Veteran Services Event')
                custom_name = self.custom_event_name
                conn_results_rotated[0][i] = custom_name
                conn_results_rotated[0] = tuple(conn_results_rotated[0])

        app = DjangoDash('Graph')  # replaces dash.Dash

        # Check if the query was valid
        validDates = self.checkInvalidQuery(conn_results_rotated)

        # If the query did not return any visits, fill the x and y axis with placeholders
        if conn_results_rotated == []:
            x_axis = [1, 2, 3, 4, 5, 6, 7, 8]
            y_axis = [1, 2, 3, 4, 5, 6, 7, 8]

        else:
            # Extract the x and y-axis from the tuple results
            x_axis = conn_results_rotated[0]
            y_axis = conn_results_rotated[1]
            x_axis = x_axis[::-1]
            y_axis = y_axis[::-1]

        # Build the Pie Chart object
        layout = Layout(title=title)
        fig = go.Figure(data=[go.Pie(labels=x_axis, values=y_axis, textinfo=self.textinfo)], layout=layout)

        # Dash instance for including a table
        if self.include_table == 'Yes' and validDates:
            header = ['Row Labels', 'Count of Location']
            x_list = list(x_axis)
            y_list = list(y_axis)
            values = [x_list, y_list]

            # Count the grand total
            total = 0
            for count in y_axis:
                total += count
            # Append the grand total to the end of the table
            x_list.append('<b>Grand Total</b>')
            y_list.append(total)

            # Setup the table object to be rendered later by Dash/Plotly
            table = go.Figure(
                data=[go.Table(header=dict(values=header, align='left'), cells=dict(values=values, align='left'))],
                layout=Layout(title=title))

            app.layout = html.Div(children=[dcc.Graph(id='table', figure=table)
                , dcc.Graph(id='figure', figure=fig, style={'height': '80vh', 'width': '80vw'}),
                                            ], style={'height': '40vh', 'width': '70vw'})
            table.update_layout(height=(220 + len(x_list) * 23))

            # Create a separate list to setup the CSV file
            new_x_list = []

            # Go though the table list and get rid of the '<b>' HTML markers -- not wanted for a CSV file
            for i, stri in enumerate(x_list):
                if isinstance(stri, int) or isinstance(stri, float):
                    replaced_str = str(stri)
                    x_list[i] = replaced_str
                    stri = replaced_str
                temp_new_string = stri.replace('<b>', '')
                new_string = temp_new_string.replace('</b>', '')
                new_x_list.append(new_string)

            # Setup the new list for the CSV file
            values = [new_x_list, y_list]

            # Generate the CSV file
            genTableFile(header, values)
        else:
            # Dash layout if the table is not included
            app.layout = html.Div(children=[
                dcc.Graph(id='figure', figure=fig, style={'height': '90vh'}),
            ], style={'height': '70vh', 'width': '70vw'})

        return app, title, validDates

# IndividualStatistic (inherits from State)
class IndividualStatistic(State):
    def __init__(self, reportGenerator, request, data):
        super(IndividualStatistic, self).__init__(reportGenerator, request, data)

    # BarGraph is the default state, but we need to check if the user wants a different type of report
    # e.g. if the user wants a Histogram, enter the histogram state
    def findState(self):
        inner_dict = self.data['form_data']
        graph_type = inner_dict[0]

        if graph_type['graphType'] == 'Pie Chart':
            self.reportGenerator.setState(self)

    # Check the graph type from the wizard, make corresponding variable conversions
    # for SQL querying
    def determineSelection(self):
        # Pull from the wizard form data
        self.inner_dict = self.data['form_data']
        self.selection_dict = self.inner_dict[1]
        self.selection = self.selection_dict['selection']
        self.title = self.selection
        self.subselection = self.selection_dict['count_options']

        # Get the appropriate category for the SQL query
        if self.selection == 'Total Usage by Location':
            self.group_by = 'location'
        elif self.selection == 'Usage by Date':
            self.group_by = 'check_in_date'
        elif self.selection == 'Classification':
            self.group_by = 'classification'
        elif self.selection == 'Major':
            self.group_by = 'major'
        elif self.selection == 'Services':
            self.group_by = 'services'
        elif self.selection == 'Benefit Chapter':
            self.group_by = 'benefit_chapter'
        elif self.selection == 'Residential Distance from Campus':
            self.group_by = 'currently_live'
        elif self.selection == 'Employment':
            self.group_by = 'employment'
        elif self.selection == 'Weekly Hours Worked':
            self.group_by = 'work_hours'
        elif self.selection == 'Number of Dependents':
            self.group_by = 'dependents'
        elif self.selection == 'Martial Status':
            self.group_by = 'marital_status'
        elif self.selection == 'Gender Identity':
            self.group_by = 'gender'
        elif self.selection == 'Parent Education':
            self.group_by = 'parent_education'
        elif self.selection == 'Break in University Attendance':
            self.group_by = 'break_in_attendance'

        # This will be used to gather the appropriate python query script from the "sql_queries" subdirectory
        # Each key represents a choice in the Wizard
        # Each key will then correspond to the python script that will run the query
        # E.g. "end_term_term_gpa" = "end_term_term_gpa.py"
        self.query_dictionary = {'End Term Semester GPA': 'end_term_term_gpa',
                                 'End Term Cumulative GPA': 'end_term_cumulative_gpa',
                                 'End Term Attempted Credits': 'end_term_attempted_credits', 'End Term Earned Credits':
                                     'end_term_earned_credits',
                                 'End Term Cumulative Completed Credits': 'end_term_credit_completion',
                                 'Benefit Chapter': 'benefit_chapter',
                                 'Residential Distance from Campus': 'currently_live', 'Employment': 'employment',
                                 'Weekly Hours Worked': 'work_hours', 'Number of Dependents': 'dependents',
                                 'Marital Status': 'marital_status', 'Gender Identity': 'gender',
                                 'Parent Education': 'parent_education',
                                 'STEM Major': 'is_stem',
                                 'Pell Grant': 'pell_grant', 'Needs Based Grants/Scholarships': 'needs_based',
                                 'Merits Based Grants/Scholarships': 'merit_based',
                                 'Federal Work Study': 'federal_work_study', 'Military Grants': 'military_grants',
                                 'Millennium Scholarship': 'millennium_scholarship',
                                 'Nevada Pre-Paid': 'nevada_prepaid',
                                 'Best Method of Contact': 'contact_method',
                                 'Break in University Attendance': 'break_in_attendance',
                                 'Total Usage by Location': 'total_usage_by_location', 'GPA': 'gpa',
                                 'Usage by Date': 'usage_by_date', 'Classification': 'classification', 'Major': 'major',
                                 'Services': 'services'}

    # Get the date range for database querying
    def determineDateRange(self):
        self.date_subdict = self.inner_dict[2]
        self.from_time = self.date_subdict['from_time']
        self.to_time = self.date_subdict['to_time']

    # Styling page from the Reports Wizard
    # Common to all graph types, but the specifics vary based on the graph selection
    def determineStyleSettings(self):
        self.style_dict = self.inner_dict[3]
        self.header_font_color = self.style_dict['header_font_color']
        self.statistic_font_color = self.style_dict['statistic_font_color']
        self.header_font_size = self.style_dict['header_font_size']
        self.statistic_font_size = self.style_dict['statistic_font_size']

    # Get the locations that the user want to track visits for
    # Ex: user will enter "VS Fitzgerald" and "VS Event"
    # This will get "VS Fitzgerald" and "VS Event" checkbox selections and store them for the query
    def determineLocationsToTrack(self):
        self.location_dict = self.inner_dict[4]
        self.location_list = self.location_dict['attendance_data']
        self.select_all = self.location_dict['select_all']
        self.use_custom_event_name = self.location_dict['use_custom_event_name']
        self.custom_event_name = self.location_dict['custom_event_name']

        # Check if the user wants to select all locations to represent this choice in the report
        # title (if not custom title)
        if self.select_all:
            self.all_locations = True
        else:
            self.all_locations = False

    # The main function that will generate the report
    def generateReport(self):
        # Get all of the user's choices from the Reports Wizard
        self.determineSelection()
        self.determineDateRange()
        self.determineStyleSettings()
        self.determineLocationsToTrack()

        conn = sqlite3.connect('vmc_tap.db');
        conn_results = []

        # Determines the default title
        # Either visits based report, or GPA-based demographics report
        if self.all_locations:
            self.title = "Count of " + self.title + ", All Locations, from " + self.from_time.strftime(
                '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
        # If the user did not select all available locations, include each location selection in the title rather than
        # "all locations"
        else:
            loc_str = ''
            for loc in self.location_list:
                if loc != self.location_list[-1]:
                    loc_str += loc + ', '
                else:
                    loc_str += loc

            # Generates a non-custom title (if custom title was not selected) for individual locations,
            self.title = "Count of " + self.title + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')

        # Determines the non-custom title depending on whether the user wants a total count, daily average, monthly
        # average, or yearly average
        if self.subselection == 'Total Count':
            new_title = 'Count of ' + self.selection + ' from ' + self.from_time.strftime(
                '%m/%d/%y') + ' to ' + self.to_time.strftime('%m/%d/%y')
        elif self.subselection == 'Daily average':
            new_title = 'Count of Daily Average ' + self.selection + ' from ' + self.from_time.strftime(
                '%m/%d/%d') + ' to ' + self.to_time.strftime('%m/%d/%y')
        elif self.subselection == 'Monthly average':
            new_title = 'Count of Monthly Average ' + self.selection + ' from ' + self.from_time.strftime(
                '%m/%d/%y') + ' to ' + self.to_time.strftime('%m/%d/%y')
        elif self.subselection == 'Yearly average':
            new_title = 'Count of Yearly Average ' + self.selection + ' from ' + self.from_time.strftime(
                '%m/%d/%y') + ' to ' + self.to_time.strftime('%m/%d/%y')

        # The max size of a location list is 2. If this is true, then show "all locations in the title"
        if len(self.location_list) == 3:
            title2 = ' Locations: All'
        else:
            title2 = ' Locations: '
            for location in self.location_list:
                title2 += location + ' '

        new_title += '\n' + title2

        # If the user opted for a custom title, get the name of the custom title
        custom_title = self.get_custom_title()
        if custom_title == '':
            title = new_title
        else:
            title = custom_title

        substr = "\""

        # Gather the user's location selections from the Reports Wizard to put them in the correct format
        # for the SQL query
        for i, location in enumerate(self.location_list):
            if i != (len(self.location_list) - 1):
                substr += location + '\' or location = \''
            else:
                substr += location

        substr += '"'

        # If the user wants to query visits over a given date range,
        # get the appropriate python script for the query, passing in the date range and locations
        # Each python script has a single function called "get_query()" but the details of the function
        # vary based on the type of query

        # Query based on total count of visitors
        if self.subselection == 'Total Count':
            self.conn_string_sql = eval(
                self.query_dictionary[self.selection] + ".get_query('" + self.from_time.strftime(
                    '%Y-%m-%d') + "', '" + self.to_time.strftime(
                    '%Y-%m-%d') + "', " + substr + ")")
        # Query based on daily average visitors over a given date range
        elif self.subselection == 'Daily average':
            self.conn_string_sql = eval(
                "ind_daily_avg.get_query('" + self.query_dictionary[self.selection] + "', '" + self.from_time.strftime(
                    '%Y-%m-%d') + "', '" + self.to_time.strftime(
                    '%Y-%m-%d') + "', " + substr + ")")
        # Monthly average visitors
        elif self.subselection == 'Monthly average':
            self.conn_string_sql = eval(
                "ind_monthly_avg.get_query('" + self.query_dictionary[
                    self.selection] + "', '" + self.from_time.strftime(
                    '%Y-%m-%d') + "', '" + self.to_time.strftime(
                    '%Y-%m-%d') + "', " + substr + ")")
        # Yearly average visitors for multiple years
        elif self.subselection == 'Yearly average':
            self.conn_string_sql = eval(
                "ind_yearly_avg.get_query('" + self.query_dictionary[
                    self.selection] + "', '" + self.from_time.strftime(
                    '%Y-%m-%d') + "', '" + self.to_time.strftime(
                    '%Y-%m-%d') + "', " + substr + ")")

        # Execute the query
        for d in conn.execute(self.conn_string_sql):
            conn_results.append(d);

        conn.close()

        # Rotates 2D array to work w/ plotly
        conn_results_rotated = list(zip(*conn_results[::-1]))

        # If the query returned valid visits
        if conn_results_rotated:
            # If the user used a custom event name
            if 'Veteran Services Event' in conn_results_rotated[0] and self.use_custom_event_name == 'Yes':
                # Replace all results returned in the query that state "Veteran Services Event" to the
                # name of the custom event specified by the user
                conn_results_rotated[0] = list(conn_results_rotated[0])
                i = conn_results_rotated[0].index('Veteran Services Event')
                custom_name = self.custom_event_name
                conn_results_rotated[0][i] = custom_name
                conn_results_rotated[0] = tuple(conn_results_rotated[0])

        app = DjangoDash('Graph')  # replaces dash.Dash

        # Check if the query was valid
        validDates = self.checkInvalidQuery(conn_results_rotated)

        # If the query did not return any visits, fill the x and y axis with placeholders
        if conn_results_rotated == []:
            x_axis = [1, 2, 3, 4, 5, 6, 7, 8]
            y_axis = [1, 2, 3, 4, 5, 6, 7, 8]

        else:
            # Extract the x and y-axis from the tuple results
            x_axis = conn_results_rotated[0]
            y_axis = conn_results_rotated[1]
            # Convert the tuples into Python lists
            x_axis = x_axis[::-1]
            y_axis = y_axis[::-1]

        # Dash instance for including a table
        header = ['Row Labels', 'Count of Location']
        x_list = list(x_axis)
        y_list = list(y_axis)
        values = [x_list, y_list]

        # Get a running total of the visits
        total = 0
        for count in y_axis:
            total += count

        # Get the grand total with HTML <b> markers to display as bold font
        x_list.append('<b>Grand Total</b>')
        y_list.append(total)

        # Setup the table object to be rendered later by Dash/Plotly
        layout = Layout(title=title)
        table = go.Figure(data=[go.Table(header=dict(values=header, align='left', height=int(self.header_font_size) * 3,
                                                     font=dict(color=self.header_font_color,
                                                               size=int(self.header_font_size))),
                                         cells=dict(values=values, align='left',
                                                    height=int(self.statistic_font_size) * 3,
                                                    font=dict(color=self.statistic_font_color,
                                                              size=int(self.statistic_font_size))))],
                          layout=Layout(title=title))

        table.update_layout(height=(220 + len(x_list) * 27))

        # Create a separate list to setup the CSV file
        new_x_list = []

        if validDates:
            # Go though the table list and get rid of the '<b>' HTML markers -- not wanted for a CSV file
            for i, stri in enumerate(x_list):
                if isinstance(stri, int) or isinstance(stri, float):
                    replaced_str = str(stri)
                    x_list[i] = replaced_str
                    stri = replaced_str
                temp_new_string = stri.replace('<b>', '')
                new_string = temp_new_string.replace('</b>', '')
                new_x_list.append(new_string)

        # Setup the new list for the CSV file
        values = [new_x_list, y_list]

        # Generate the CSV file
        genTableFile(header, values)

        # Dash layout for the individual statistic table
        app.layout = html.Div(children=[dcc.Graph(id='table', figure=table, style={'height': '110vh'})
                                        ], style={'height': '110vh', 'width': '70vw'})


        return app, title, validDates

# ScatterPlot (inherits from State)
# Used for scatter plots and line graphs
class ScatterPlot(State):
    def __init__(self, reportGenerator, request, data):
        super(ScatterPlot, self).__init__(reportGenerator, request, data)

    # BarGraph is the default state, but we need to check if the user wants a different type of report
    # e.g. if the user wants a Histogram, enter the histogram state
    def findState(self):
        # Wizard form data is based on a nested dictionary structure
        # Eeach of the wizard form fields represent a key to the dictionary
        inner_dict = self.data['form_data']
        graph_type = inner_dict[0]

        if graph_type['graphType'] == 'Line and/or Scatter':
            self.reportGenerator.setState(self)

    # Check the graph type from the wizard, make corresponding variable conversions
    # for SQL querying
    def determineSelection(self):
        # Pull from the wizard form data
        self.inner_dict = self.data['form_data']
        self.selection_dict = self.inner_dict[1]
        self.selection = self.selection_dict['selection']
        self.title = self.selection
        self.include_table = self.selection_dict['include_table']
        self.report_type = self.selection_dict['report_type']
        self.category = self.selection_dict['category']
        self.gpa_to_compare = self.selection_dict['gpa_to_compare']

        if self.report_type == 'Count visits over time':
            self.title = self.selection
        elif self.report_type == 'Compare GPA against demographics':
            self.title = self.category

        # Convert selection into query '*' for SQL
        # This will be used to gather the appropriate python query script from the "sql_queries" subdirectory
        # Each key represents a choice in the Wizard
        # Each key will then correspond to the python script that will run the query
        # E.g. "end_term_term_gpa" = "end_term_term_gpa.py"
        self.query_dictionary = {'Benefit Chapter': 'benefit_chapter',
                                 'Residential Distance from Campus': 'currently_live', 'Employment': 'employment',
                                 'Weekly Hours Worked': 'work_hours', 'Number of Dependents': 'dependents',
                                 'Marital Status': 'marital_status', 'Gender Identity': 'gender',
                                 'Parent Education': 'parent_education', 'STEM Major': 'is_stem',
                                 'Pell Grant': 'pell_grant', 'Needs Based Grants/Scholarships': 'needs_based',
                                 'Merits Based Grants/Scholarships': 'merit_based',
                                 'Federal Work Study': 'federal_work_study', 'Military Grants': 'military_grants',
                                 'Millennium Scholarship': 'millennium_scholarship',
                                 'Nevada Pre-Paid': 'nevada_prepaid',
                                 'Best Method of Contact': 'contact_method',
                                 'Break in University Attendance': 'break_in_attendance',
                                 'Total Usage by Location': 'total_usage_by_location', 'GPA': 'gpa',
                                 'Usage by Date': 'usage_by_date', 'Classification': 'classification', 'Major': 'major',
                                 'Services': 'services'}

        # If the user wants a GPA vs. demographics report, this dictionary will be used to
        # gather the approrpiate python script from the "sql_queries" subdirectory
        self.gpa_dictionary = {'Average end term Semester GPA': 'end_term_term_gpa',
                               'Average end term Cumulative GPA': 'end_term_cumulative_gpa',
                               'Average end term Attempted Credits': 'end_term_attempted_credits',
                               'Average end term Earned Credits': 'end_term_earned_credits',
                               'Average end term Cumulative Completed Credits': 'end_term_credit_completion'}

    # Get the date range for database querying
    def determineDateRange(self):
        self.date_subdict = self.inner_dict[2]
        self.from_time = self.date_subdict['from_time']
        self.to_time = self.date_subdict['to_time']

    # Styling page from the Reports Wizard
    # Common to all graph types, but the specifics vary based on the graph selection
    def determineStyleSettings(self):
        self.style_dict = self.inner_dict[3]
        self.bar_color = self.style_dict['select_dot_color']
        self.autoscale = self.style_dict['autoscale']
        if self.autoscale == 'No':
            self.max_count = self.style_dict['max_count']
            self.increment_by = self.style_dict['increment_by']
        if self.style_dict['display_as'] == 'Dots':
            self.mode = 'markers'
        elif self.style_dict['display_as'] == 'Lines':
            self.mode = 'lines'
        elif self.style_dict['display_as'] == 'Dots and Lines':
            self.mode = 'lines+markers'

    # Get the locations that the user want to track visits for
    # Ex: user will enter "VS Fitzgerald" and "VS Event"
    # This will get "VS Fitzgerald" and "VS Event" checkbox selections and store them for the query
    def determineLocationsToTrack(self):
        self.location_dict = self.inner_dict[4]
        self.location_list = self.location_dict['attendance_data']
        self.select_all = self.location_dict['select_all']
        self.use_custom_event_name = self.location_dict['use_custom_event_name']
        self.custom_event_name = self.location_dict['custom_event_name']
        # Check if the user wants to select all locations to represent this choice in the report
        # title (if not custom title)
        if self.select_all:
            self.all_locations = True
        else:
            self.all_locations = False

    # The main function that will generate the report
    def generateReport(self):
        # Get all of the user's choices from the Reports Wizard
        self.determineSelection()
        self.determineDateRange()
        self.determineStyleSettings()
        self.determineLocationsToTrack()

        conn = sqlite3.connect('vmc_tap.db')
        conn_results = []

        # Determines the default title
        # Either visits based report, or GPA-based demographics report
        if self.all_locations:
            if self.report_type == 'Count visits over time':
                self.title = "Count of " + self.title + ", all Locations from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
            elif self.report_type == 'Compare GPA against demographics':
                self.title = self.gpa_to_compare + " by " + self.category + ", all Locations, from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
        # If the user did not select all available locations, include each location selection in the title rather than
        # "all locations"
        else:
            loc_str = ''
            for loc in self.location_list:
                if loc != self.location_list[-1]:
                    loc_str += loc + ', '
                else:
                    loc_str += loc
            # Generates a non-custom title (if custom title was not selected) for individual locations,
            # if the user did not select "all locations"
            if self.report_type == 'Count visits over time':
                self.title = "Count of " + self.title + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
            elif self.report_type == 'Compare GPA against demographics':
                self.title = self.gpa_to_compare + " by " + self.category + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')

        # If the user opted for a custom title, get the name of the custom title
        custom_title = self.get_custom_title()
        if custom_title == '':
            title = self.title
        else:
            title = custom_title

        substr = "\""

        # Gather the user's location selections from the Reports Wizard to put them in the correct format
        # for the SQL query
        for i, location in enumerate(self.location_list):
            if i != (len(self.location_list) - 1):
                substr += location + '\' or location = \''
            else:
                substr += location

        substr += '"'

        # If the user wants to query visits over a given date range,
        # get the appropriate python script for the query, passing in the date range and locations
        # Each python script has a single function called "get_query()" but the details of the function
        # vary based on the type of query
        if self.report_type == 'Count visits over time':
            self.conn_string_sql = eval(
                self.query_dictionary[self.selection] + ".get_query('" + self.from_time.strftime(
                    '%Y-%m-%d') + "', '" + self.to_time.strftime(
                    '%Y-%m-%d') + "', " + substr + ")")
        # Same as above, except the user is querying GPA vs. demographics instead of visits
        elif self.report_type == 'Compare GPA against demographics':
            self.conn_string_sql = eval(
                self.query_dictionary[self.category] + "_gpa.get_query('" + self.gpa_dictionary[
                    self.gpa_to_compare] + "', '" + self.from_time.strftime(

                    '%Y-%m-%d') + "', '" + self.to_time.strftime(
                    '%Y-%m-%d') + "', " + substr + ")")

        # Execute the database query via the SQL command obtained
        for d in conn.execute(self.conn_string_sql):
            conn_results.append(d);

        conn.close()

        # Rotates 2D array to work w/ plotly
        conn_results_rotated = list(zip(*conn_results[::-1]))

        # If the query returned valid visits
        if conn_results_rotated:
            # If the user used a custom event name
            if 'Veteran Services Event' in conn_results_rotated[0] and self.use_custom_event_name == 'Yes':
                # Replace all results returned in the query that state "Veteran Services Event" to the
                # name of the custom event specified by the user
                conn_results_rotated[0] = list(conn_results_rotated[0])
                i = conn_results_rotated[0].index('Veteran Services Event')
                custom_name = self.custom_event_name
                conn_results_rotated[0][i] = custom_name
                conn_results_rotated[0] = tuple(conn_results_rotated[0])

        app = DjangoDash('Graph')  # replaces dash.Dash

        # Check if the query was valid
        validDates = self.checkInvalidQuery(conn_results_rotated)

        # If the query did not return any visits, fill the x and y axis with placeholders
        if conn_results_rotated == []:
            x_axis = [1, 2, 3, 4, 5, 6, 7, 8]
            y_axis = [1, 2, 3, 4, 5, 6, 7, 8]
        else:
            # Extract the x and y-axis from the tuple results
            x_axis = conn_results_rotated[0]
            y_axis = conn_results_rotated[1]
            x_axis = x_axis[::-1]
            y_axis = y_axis[::-1]

        # If autoscaling is not enabled by the user, we need to set the max count of the y-axis
        if self.autoscale != 'Yes':
            layout = go.Layout(title=title, yaxis=dict(range=[0, self.max_count]))
        else:
            layout = Layout(title=title)

        # Setup the bar graph object to display via Plotly/Dash
        # The "self.mode" is gathered from the Reports Wizard to decide whether the graph will be a line graph,
        # scatter plot, or both, depending on user input
        fig = go.Figure(
            data=[go.Scatter(x=x_axis, y=y_axis, mode=self.mode, marker=dict(color=self.bar_color.lower()))],
            layout=layout)

        # Now implement the custom scaling if enabled
        if self.autoscale != 'Yes':
            fig.update_yaxes(dtick=self.increment_by)

        # Dash instance for including a table
        if self.include_table == 'Yes' and validDates:
            header = ['Row Labels', 'Count of Location']
            x_list = list(x_axis)
            y_list = list(y_axis)
            values = [x_list, y_list]

            # If we are counting visits over time, get the grand total
            if self.report_type == 'Count visits over time':
                total = 0
                for count in y_axis:
                    total += count
                # Include header for the grand total, including HTML bold "<b>" marker
                x_list.append('<b>Grand Total</b>')
                y_list.append(total)
            # If we are getting averages, get the average instead of a grand total
            elif self.report_type == 'Compare GPA against demographics':
                total_values = len(y_list)
                total = 0
                for count in y_axis:
                    total += count
                # Include header for the total average, including HTML bold "<b>" marker
                x_list.append('<b>Total Average<b>')
                total /= total_values
                # Round off the total average to two decimal places
                y_list.append(round(total, 2))

            # Setup the table object to be rendered later by Dash/Plotly
            table = go.Figure(
                data=[go.Table(header=dict(values=header, align='left'), cells=dict(values=values, align='left'))],
                layout=Layout(title=title))
            table.update_layout(height=(220 + len(x_list) * 23))

            app.layout = html.Div(children=[dcc.Graph(id='table', figure=table)
                , dcc.Graph(id='figure', figure=fig, style={'height': '80vh', 'width': '80vw'}),
                                            ], style={'height': '40vh', 'width': '70vw'})

            # Create a separate list to setup the CSV file
            new_x_list = []

            # Go though the table list and get rid of the '<b>' HTML markers -- not wanted for a CSV file
            for i, stri in enumerate(x_list):
                if isinstance(stri, int) or isinstance(stri, float):
                    replaced_str = str(stri)
                    x_list[i] = replaced_str
                    stri = replaced_str
                temp_new_string = stri.replace('<b>', '')
                new_string = temp_new_string.replace('</b>', '')
                new_x_list.append(new_string)

            # Setup the new list for the CSV file
            values = [new_x_list, y_list]

            # Generate the CSV file
            genTableFile(header, values)

        # Dash layout if the table is not included
        else:
            app.layout = html.Div(children=[
                dcc.Graph(id='figure', figure=fig, style={'height': '90vh'}),
            ], style={'height': '70vh', 'width': '70vw'})

        return app, title, validDates

# Sets up the report object based on form data that was entered by the user in the Reports Wizard
# Returns the rendered HTML page with the report output
def getReport(request):
    # Get the form data from the Reports Wizard
    data = pageViews.preset_storage
    inner_dict = data['form_data']
    graph_type_dict = inner_dict[0]
    graph_type = graph_type_dict['graphType']
    reportGenerator = ReportGenerator(request, data)
    app, title, valid_dates = reportGenerator.generateReport()

    # If the query returned visits, go ahead and render the report
    if valid_dates:
        return render(request, 'visualizations/getReport.html', context={'graphTitle': title})
    # If no visits were returned from the query, render an HTML form that asks the user for the different date range
    elif request.method == 'POST':
        form = TimeFrame(request.POST)
        if form.is_valid():
            from_time = request.POST.get('from_time')
            to_time = request.POST.get('to_time')

            from_time = datetime.strptime(from_time, '%m/%d/%Y')
            to_time = datetime.strptime(to_time, '%m/%d/%Y')
            if graph_type == 'Bar Graph':
                data = dateQueryCorrection(data, from_time, to_time)
            elif graph_type == 'Histogram':
                data = dateQueryCorrection(data, from_time, to_time)
            elif graph_type == 'Line and/or Scatter':
                data = dateQueryCorrection(data, from_time, to_time)
            elif graph_type == 'Pie Chart':
                data = dateQueryCorrection(data, from_time, to_time)
            elif graph_type == 'Individual Statistic':
                data = dateQueryCorrection(data, from_time, to_time)
            reportGenerator.setData(data)
            app, title, valid_dates = reportGenerator.generateReport()
            # If the new dates are valid, go ahead and render the report
            if valid_dates:
                return render(request, 'visualizations/getReport.html', context={'graphTitle': title})
            # Handling for empty date form submission
            else:
                form = TimeFrame()
                return render(request, 'visualizations/queryCorrection.html', context={'form': form})
        # If the user entered a date range that returned no visits, render the HTML form that asks for the new
        # date range
        else:
            return render(request, 'visualizations/queryCorrection.html', context={'form': form})
    else:
        form = TimeFrame()
        return render(request, 'visualizations/queryCorrection.html', context={'form': form})


# If the user enters dates that return no visits, this will handle the new dates that
# the user enters
# Returns the new date range
def dateQueryCorrection(data, new_from_time, new_to_time):
    inner_dict = data['form_data']
    date_subdict = inner_dict[2]
    date_subdict['from_time'] = new_from_time
    date_subdict['to_time'] = new_to_time

    return data


# Convert bar graph preset data back into dictionary format to prepare send it to the report generator
# Returns the data in dictionary format
def getBarGraphPreset(presetModel, from_time, to_time):
    from_time = datetime.strptime(from_time, '%m-%d-%Y')
    to_time = datetime.strptime(to_time, '%m-%d-%Y')
    report_data = {}
    report_data['form_data'] = []
    inner_list = report_data['form_data']
    inner_list.append({'graphType': 'Bar Graph', 'title': presetModel.title})
    inner_list.append({'selection': presetModel.selection, 'include_table': presetModel.include_table,
                       'report_type': presetModel.report_type, 'category': presetModel.category,
                       'gpa_to_compare': presetModel.gpa_to_compare})
    inner_list.append({'from_time': from_time, 'to_time': to_time})
    if presetModel.autoscale == 'Yes':
        inner_list.append({'select_bar_color': presetModel.select_bar_color, 'autoscale': presetModel.autoscale,
                           'show_multiple_bars_by_location': presetModel.multiple_bars, 'max_count': None,
                           'increment_by': None})
    else:
        inner_list.append({'select_bar_color': presetModel.select_bar_color, 'autoscale': presetModel.autoscale,
                           'show_multiple_bars_by_location': presetModel.multiple_bars,
                           'max_count': presetModel.max_count, 'increment_by': presetModel.increment_by})

    inner_list.append({'attendance_data': presetModel.locations.split(','), 'select_all': presetModel.select_all,
                       'use_custom_event_name': presetModel.use_custom_event_name,
                       'custom_event_name': presetModel.custom_event_name})

    return report_data


# Convert histogram preset data back into dictionary format to prepare send it to the report generator
# Returns the data in dictionary format
def getHistogramPreset(presetModel, from_time, to_time):
    from_time = datetime.strptime(from_time, '%m-%d-%Y')
    to_time = datetime.strptime(to_time, '%m-%d-%Y')
    report_data = {}
    report_data['form_data'] = []
    inner_list = report_data['form_data']
    inner_list.append({'graphType': 'Histogram', 'title': presetModel.title})
    inner_list.append({'time_units': presetModel.time_units, 'include_table': presetModel.include_table})
    inner_list.append({'from_time': from_time, 'to_time': to_time})
    if presetModel.autoscale == 'Yes':
        inner_list.append({'select_bar_color': presetModel.select_bar_color, 'autoscale': presetModel.autoscale,
                           'max_count': None, 'increment_by': None})
    else:
        inner_list.append({'select_bar_color': presetModel.select_bar_color, 'autoscale': presetModel.autoscale,
                           'max_count': presetModel.max_count, 'increment_by': presetModel.increment_by})

    inner_list.append({'attendance_data': presetModel.locations.split(','), 'select_all': presetModel.select_all,
                       'use_custom_event_name': presetModel.use_custom_event_name,
                       'custom_event_name': presetModel.custom_event_name})

    return report_data

# Convert line graph/scatter plot preset data back into dictionary format to prepare send it to the report generator
# Returns the data in dictionary format
def getLineScatterPreset(presetModel, from_time, to_time):
    from_time = datetime.strptime(from_time, '%m-%d-%Y')
    to_time = datetime.strptime(to_time, '%m-%d-%Y')
    report_data = {}
    report_data['form_data'] = []
    inner_list = report_data['form_data']
    inner_list.append({'graphType': 'Line and/or Scatter', 'title': presetModel.title})
    inner_list.append({'selection': presetModel.selection, 'include_table': presetModel.include_table,
                       'report_type': presetModel.report_type, 'category': presetModel.category,
                       'gpa_to_compare': presetModel.gpa_to_compare})
    inner_list.append({'from_time': from_time, 'to_time': to_time})
    if presetModel.autoscale == 'Yes':
        inner_list.append({'autoscale': presetModel.autoscale, 'max_count': None,
                           'increment_by': None, 'select_dot_color': presetModel.dot_color,
                           'display_as': presetModel.display_options})
    else:
        inner_list.append({'autoscale': presetModel.autoscale, 'max_count': presetModel.max_count,
                           'increment_by': presetModel.increment_by, 'select_dot_color': presetModel.dot_color,
                           'display_as': presetModel.display_options})

    inner_list.append({'attendance_data': presetModel.locations.split(','), 'select_all': presetModel.select_all,
                       'use_custom_event_name': presetModel.use_custom_event_name,
                       'custom_event_name': presetModel.custom_event_name})

    return report_data

# Convert pie chart preset data back into dictionary format to prepare send it to the report generator
# Returns the data in dictionary format
def getPieChartPreset(presetModel, from_time, to_time):
    from_time = datetime.strptime(from_time, '%m-%d-%Y')
    to_time = datetime.strptime(to_time, '%m-%d-%Y')
    report_data = {}
    report_data['form_data'] = []
    inner_list = report_data['form_data']
    inner_list.append({'graphType': 'Pie Chart', 'title': presetModel.title})
    inner_list.append({'selection': presetModel.selection, 'include_table': presetModel.include_table})
    inner_list.append({'from_time': from_time, 'to_time': to_time})
    inner_list.append({'Data_units': presetModel.data_units})
    inner_list.append({'attendance_data': presetModel.locations.split(','), 'select_all': presetModel.select_all,
                       'use_custom_event_name': presetModel.use_custom_event_name,
                       'custom_event_name': presetModel.custom_event_name})

    return report_data

# Convert individual statistic preset data back into dictionary format to prepare send it to the report generator
# Returns the data in dictionary format
def getIndividualStatisticPreset(presetModel, from_time, to_time):
    from_time = datetime.strptime(from_time, '%m-%d-%Y')
    to_time = datetime.strptime(to_time, '%m-%d-%Y')
    report_data = {}
    report_data['form_data'] = []
    inner_list = report_data['form_data']
    inner_list.append({'graphType': 'Individual Statistic', 'title': presetModel.title})
    inner_list.append({'selection': presetModel.selection, 'count_options': presetModel.count_options})
    inner_list.append({'from_time': from_time, 'to_time': to_time})
    inner_list.append({'header_font_color': presetModel.header_font_color,
                       'statistic_font_color': presetModel.statistic_font_color,
                       'header_font_size': presetModel.header_font_size,
                       'statistic_font_size': presetModel.statistic_font_size})

    inner_list.append({'attendance_data': presetModel.locations.split(','), 'select_all': presetModel.select_all,
                       'use_custom_event_name': presetModel.use_custom_event_name,
                       'custom_event_name': presetModel.custom_event_name})

    return report_data

# When the user selects from a saved preset on the "presets" page, this will
# obtain the correct preset from the database and return the rendered report to the user
def presetReport(request, preset_name, from_time, to_time):
    preset_name = unquote(preset_name)
    # Get the preset object
    preset = ReportPresets.objects.get(pk=preset_name)
    # Get the appropriate database data depending on the graph type
    if preset.graph_type == 'Bar Graph':
        data_dict = getBarGraphPreset(preset, from_time, to_time)
    elif preset.graph_type == 'Histogram':
        data_dict = getHistogramPreset(preset, from_time, to_time)
    elif preset.graph_type == 'Line and/or Scatter':
        data_dict = getLineScatterPreset(preset, from_time, to_time)
    elif preset.graph_type == 'Pie Chart':
        data_dict = getPieChartPreset(preset, from_time, to_time)
    elif preset.graph_type == 'Individual Statistic':
        data_dict = getIndividualStatisticPreset(preset, from_time, to_time)

    reportGenerator = ReportGenerator(request, data_dict)
    # Get the report object
    app, title, valid_dates = reportGenerator.generateReport()

    # If the dates entered by the user returned visits, render the report
    if valid_dates:
        return render(request, 'visualizations/getReport.html', context={'graphTitle': title})
    # Else render the HTML form to get a new date range from the user
    else:
        form = TimeFrame()
        pageViews.preset_storage = data_dict
        return render(request, 'visualizations/queryCorrection.html', context={'form': form})

# Generate the CSV file for the user
# Takes the existing table in the report and converts it to a CSV file
def genTableFile(header, values):
    rows = zip(values[0], values[1])
    with open(os.path.join(os.getcwd(), 'table.csv'), 'w+', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(header)
        for value in rows:
            csvwriter.writerow(value)
        csvfile.close()

# If the user decides to download the CSV file, this function will
# handle the download request and download the file to the user's browser
def downloadFile(request):
    path = os.path.join(os.getcwd(), 'table.csv')

    file = open(path, 'r')
    response = HttpResponse(file, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="%s"' % 'table.csv'

    os.remove(path)

    print('Generating table file at:', path)

    return response
