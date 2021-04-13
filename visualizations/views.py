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
import sqlite3

import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objects as go

from django_plotly_dash import DjangoDash

import csv

import os;

print(os.path.dirname(__file__))
for module in os.listdir(os.path.dirname(__file__) + '/sql_queries'):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    exec('from .sql_queries import ' + module[:-3] + ' as ' + module[:-3]);
del module;


class emptyList(Exception):
    pass


class ReportGenerator():
    def __init__(self, request, data):
        self.request = request
        self.data = data
        self.barGraph = BarGraph(self, self.request, self.data)
        # To be implemented later
        # self.histogram = Histogram(data, request, self)
        # self.lineGraph = State(data, request, self)
        # self.pieChart = State(data, request, self)
        # self.scatterPlot = State(data, request, self)
        # self.individualStatistic = State(data, request, self)

        self.state = self.barGraph
        self.state.findState()

        # TODO remove this later
        print(data)

    def setState(self, state):
        self.state = state

    def setData(self, data):
        self.data = data

    def generateReport(self):
        app, title, validDates = self.state.generateReport()
        return app, title, validDates


class State:

    def __init__(self, reportGenerator, request, data):
        self.reportGenerator = reportGenerator
        self.request = request
        self.data = data

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

    def get_custom_title(self):
        form_dict = self.data['form_data']
        inner_dict = form_dict[0]
        custom_title = inner_dict['title']

        return custom_title

    def checkInvalidQuery(self, results):
        if not results:
            return False
        else:
            return True


class BarGraph(State):
    def __init__(self, reportGenerator, request, data):
        super(BarGraph, self).__init__(reportGenerator, request, data)

    def findState(self):
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

    def determineStyleSettings(self):
        self.style_dict = self.inner_dict[3]
        self.bar_color = self.style_dict['select_bar_color']
        self.autoscale = self.style_dict['autoscale']
        if self.autoscale == 'No':
            self.max_count = self.style_dict['max_count']
            self.increment_by = self.style_dict['increment_by']
        self.show_multiple_bars = self.style_dict['show_multiple_bars_by_location']

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

    def generateReport(self):
        self.determineSelection()
        self.determineDateRange()
        self.determineStyleSettings()
        self.determineLocationsToTrack()

        if self.show_multiple_bars == 'No':
            app, title, validDates = self.generateSingleBars()
            return app, title, validDates
        elif self.show_multiple_bars == 'Yes':
            app, title, validDates = self.generateGroupedBars()
            return app, title, validDates

    def generateSingleBars(self):
        conn = sqlite3.connect('vmc_tap.db');
        conn_results = []

        if self.all_locations:
            if self.report_type == 'Count visits over time':
                self.title = "Count of " + self.title + ", all Locations from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
            elif self.report_type == 'Compare GPA against demographics':
                self.title = self.gpa_to_compare + " by " + self.category + ", all Locations, from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
        else:
            loc_str = ''
            for loc in self.location_list:
                if loc != self.location_list[-1]:
                    loc_str += loc + ', '
                else:
                    loc_str += loc

            if self.report_type == 'Count visits over time':
                self.title = "Count of " + self.title + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
            elif self.report_type == 'Compare GPA against demographics':
                self.title = self.gpa_to_compare + " by " + self.category + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')

        custom_title = self.get_custom_title()
        if custom_title == '':
            title = self.title
        else:
            title = custom_title

        substr = "\""

        for i, location in enumerate(self.location_list):
            if i != (len(self.location_list) - 1):
                substr += location + '\' or location = \''
            else:
                substr += location

        substr += '"'

        if self.report_type == 'Count visits over time':
            self.conn_string_sql = eval(
                self.query_dictionary[self.selection] + ".get_query('" + self.from_time.strftime(
                    '%Y-%m-%d') + "', '" + self.to_time.strftime(
                    '%Y-%m-%d') + "', " + substr + ")")
        elif self.report_type == 'Compare GPA against demographics':
            self.conn_string_sql = eval(
                self.query_dictionary[self.category] + "_gpa.get_query('" + self.gpa_dictionary[
                    self.gpa_to_compare] + "', '" + self.from_time.strftime(

                    '%Y-%m-%d') + "', '" + self.to_time.strftime(
                    '%Y-%m-%d') + "', " + substr + ")")

        print('location_list: ', self.location_list)

        # conn_string_sql = "select location, count(" + self.selection + ") from visits group by location;"

        print('conn_string_sql', self.conn_string_sql)
        #       print('conn.execute: ', conn.execute(conn_string_sql))

        for d in conn.execute(self.conn_string_sql):
            conn_results.append(d);

        conn.close()

        # Rotates 2D array to work w/ plotly
        conn_results_rotated = list(zip(*conn_results[::-1]))
        print('Conn results_rotated:', conn_results_rotated)

        if conn_results_rotated:
            if 'Event' in conn_results_rotated[0] and self.use_custom_event_name == 'Yes':
                conn_results_rotated[0] = list(conn_results_rotated[0])
                i = conn_results_rotated[0].index('Event')
                custom_name = self.custom_event_name
                conn_results_rotated[0][i] = custom_name
                conn_results_rotated[0] = tuple(conn_results_rotated[0])

        print('Conn results_rotated back into a tuple', conn_results_rotated)

        app = DjangoDash('Graph')  # replaces dash.Dash

        # print('conn_results_rotated: ', conn_results_rotated)

        validDates = self.checkInvalidQuery(conn_results_rotated)

        if not validDates:
            x_axis = [1, 2, 3, 4, 5, 6, 7, 8]
            y_axis = [1, 2, 3, 4, 5, 6, 7, 8]
        else:
            x_axis = conn_results_rotated[0]
            y_axis = conn_results_rotated[1]
            x_axis = x_axis[::-1]
            y_axis = y_axis[::-1]
            # for tuple in conn_results:
            #    x_axis.append(tuple[0])
            #   y_axis.append(tuple[1])

        # If autoscaling is not enabled by the user, we need to set the max count of the y-axis
        if self.autoscale != 'Yes':
            layout = go.Layout(title=title, yaxis=dict(range=[0, self.max_count]))
        else:
            layout = Layout(title=title)

        fig = go.Figure(data=[go.Bar(x=x_axis, y=y_axis, marker=dict(color=self.bar_color.lower()))], layout=layout)
        fig.update_xaxes(type='category')

        # Now implement the custom scaling if enabled
        if self.autoscale != 'Yes':
            fig.update_yaxes(dtick=self.increment_by)
        # graph = [Bar(x=x_axis,y=y_axis)]
        # layout = Layout(title='Length of Visits',xaxis=dict(title='Length (min)'),yaxis=dict(title='# of Visits'))
        # fig = Figure(data=graph,layout=layout)
        # plot_div = plot(fig,output_type='div',show_link=False,link_text="")

        # Dash instance for includng a table
        if self.include_table == 'Yes' and validDates:
            header = ['Row Labels', 'Count of Location']
            x_list = list(x_axis)
            y_list = list(y_axis)

            if self.report_type == 'Count visits over time':
                total = 0
                for count in y_axis:
                    total += count

                x_list.append('<b>Grand Total</b>')
                y_list.append(total)
            elif self.report_type == 'Compare GPA against demographics':
                total_values = len(y_list)
                total = 0
                for count in y_axis:
                    total += count
                x_list.append('<b>Total Average<b>')
                total /= total_values
                y_list.append(round(total, 2))

            print('x_list:', x_list)

            values = [x_list, y_list]

            table = go.Figure(data=[go.Table(header=dict(values=header), cells=dict(values=values))],
                              layout=Layout(title=title))
            table.update_layout(height=(200 + len(x_list) * 23))

            new_x_list = []

            for i, stri in enumerate(x_list):
                if isinstance(stri, int) or isinstance(stri, float):
                    replaced_str = str(stri)
                    x_list[i] = replaced_str
                    stri = replaced_str
                temp_new_string = stri.replace('<b>', '')
                new_string = temp_new_string.replace('</b>', '')
                new_x_list.append(new_string)

            values = [new_x_list, y_list]

            genTableFile(header, values)

            app.layout = html.Div(children=[dcc.Graph(id='table', figure=table)
                , dcc.Graph(id='figure', figure=fig, style={'height': '40vh'}),
                                            ], style={'height': '40vh', 'width': '70vw'})
        else:
            app.layout = html.Div(children=[
                dcc.Graph(id='figure', figure=fig, style={'height': '90vh'}),
            ], style={'height': '70vh', 'width': '70vw'})

        return app, title, validDates

    def generateGroupedBars(self):

        conn = sqlite3.connect('vmc_tap.db');
        conn_results = []

        if self.all_locations:
            if self.report_type == 'Count visits over time':
                self.title = "Count of " + self.title + ", all Locations from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
            elif self.report_type == 'Compare GPA against demographics':
                self.title = self.gpa_to_compare + " by " + self.category + ", all Locations, from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
        else:
            loc_str = ''
            for loc in self.location_list:
                if loc != self.location_list[-1]:
                    loc_str += loc + ', '
                else:
                    loc_str += loc

            if self.report_type == 'Count visits over time':
                self.title = "Count of " + self.title + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
            elif self.report_type == 'Compare GPA against demographics':
                self.title = self.gpa_to_compare + " by " + self.category + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')

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
        if self.report_type == 'Count visits over time':
            for location in self.location_list:
                loc_str = "'"
                loc_str += location + "'"
                self.conn_string_sql.append(
                    eval(self.query_dictionary[self.selection] + ".get_query('" + self.from_time.strftime(
                        '%Y-%m-%d') + "', '" + self.to_time.strftime(
                        '%Y-%m-%d') + "', " + loc_str + ")"))
        elif self.report_type == 'Compare GPA against demographics':
            for location in self.location_list:
                loc_str = "'"
                loc_str += location + "'"
                self.conn_string_sql.append(eval(
                    self.query_dictionary[self.category] + "_gpa.get_query('" + self.gpa_dictionary[
                        self.gpa_to_compare] + "', '" + self.from_time.strftime(

                        '%Y-%m-%d') + "', '" + self.to_time.strftime(
                        '%Y-%m-%d') + "', " + loc_str + ")"))

            # self.conn_string_sql.append(
            #   "select " + self.group_by + ", count(" + self.selection + ") from visits where (location = \'" + location + "\') and check_in_date >= \'" + self.from_time.strftime(
            #      '%Y-%m-%d') + "\' and check_in_date <= \'" + self.to_time.strftime(
            #   '%Y-%m-%d') + "\' group by " + self.group_by + ";")
        print('location_list: ', self.location_list)

        # conn_string_sql = "select location, count(" + self.selection + ") from visits group by location;"

        print('conn_string_sql', self.conn_string_sql)
        #       print('conn.execute: ', conn.execute(conn_string_sql))

        location_results = []
        valid_dates = []

        for i, location in enumerate(self.location_list):
            conn_results = []
            for d in conn.execute(self.conn_string_sql[i]):
                conn_results.append(d)
            # Rotates 2D array to work w/ plotly
            conn_results_rotated = list(zip(*conn_results[::-1]))
            if conn_results_rotated:
                if 'Event' in conn_results_rotated[0] and self.use_custom_event_name == 'Yes':
                    conn_results_rotated[0] = list(conn_results_rotated[0])
                    i = conn_results_rotated[0].index('Event')
                    custom_name = self.custom_event_name
                    conn_results_rotated[0][i] = custom_name
                    conn_results_rotated[0] = tuple(conn_results_rotated[0])
                location_results.append(conn_results_rotated)
            valid_dates.append(self.checkInvalidQuery(conn_results_rotated))

        conn.close()

        print('Conn results_rotated:', conn_results_rotated)

        app = DjangoDash('Graph')  # replaces dash.Dash

        y_axis = []
        x_axis = []
        validDates = True
        for i, location in enumerate(self.location_list):
            if not valid_dates[i]:
                validDates = False
                x_axis.append([1, 2, 3, 4, 5, 6, 7, 8])
                y_axis.append([1, 2, 3, 4, 5, 6, 7, 8])
            else:
                x_results = location_results[i][0]
                y_results = location_results[i][1]
                x_results = x_results[::-1]
                y_results = y_results[::-1]
                x_axis.append(x_results)
                y_axis.append(y_results)
            # for tuple in conn_results:
            #    x_axis.append(tuple[0])
            #   y_axis.append(tuple[1])

        # If autoscaling is not enabled by the user, we need to set the max count of the y-axis
        if self.autoscale != 'Yes':
            layout = go.Layout(title=title, yaxis=dict(range=[0, self.max_count]))
        else:
            layout = Layout(title=title)

        # fig = go.Figure(data=[go.Bar(x=x_axis, y=y_axis, marker=dict(color=self.bar_color.lower()))], layout=layout)

        data_list = []
        for i, location in enumerate(self.location_list):
            if location == 'Event' and self.use_custom_event_name == 'Yes':
                data_list.append(go.Bar(name=self.custom_event_name, x=x_axis[i], y=y_axis[i]))
            else:
                data_list.append(go.Bar(name=location, x=x_axis[i], y=y_axis[i]))

        print('data_list', data_list)

        fig = go.Figure(data=data_list, layout=layout)
        # Now implement the custom scaling if enabled
        if self.autoscale != 'Yes':
            fig.update_yaxes(dtick=self.increment_by)
        # graph = [Bar(x=x_axis,y=y_axis)]
        # layout = Layout(title='Length of Visits',xaxis=dict(title='Length (min)'),yaxis=dict(title='# of Visits'))
        # fig = Figure(data=graph,layout=layout)
        # plot_div = plot(fig,output_type='div',show_link=False,link_text="")

        # Dash instance for includng a table
        if self.include_table == 'Yes':
            header = ['Row Labels', 'Count of Location']
            x_list = []
            y_list = []

            for i, location in enumerate(self.location_list):
                x_list.append(list(x_axis[i]))
                y_list.append(list(y_axis[i]))

            # x_list = list(x_axis)
            # y_list = list(y_axis)

            running_total = 0
            print('x_list', x_list)
            print('y_list', y_list)
            for i, location in enumerate(self.location_list):
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

            if conn_results_rotated[0]:
                if 'Event' in conn_results_rotated[0] and self.use_custom_event_name == 'Yes':
                    i = flattened_x_list.index('Event')
                    flattened_x_list[i] = self.custom_event_name

            flattened_y_list = [value for loc in y_list for value in loc]
            # End of reference -----------------------------------------------------------------------------

            flattened_x_list.append('<b>Grand Total</b>')

            if self.report_type == 'Compare GPA against demographics':
                running_total /= len(self.location_list)

            flattened_y_list.append(round(running_total, 2))

            values = [flattened_x_list, flattened_y_list]
            table = go.Figure(data=[go.Table(header=dict(values=header), cells=dict(values=values))],
                              layout=Layout(title=title))
            table.update_layout(height=(200 + len(flattened_x_list) * 25))

            new_x_list = []

            for value in flattened_x_list:
                if isinstance(value, str):
                    temp_new_string = value.replace('<b>', '')
                    new_string = temp_new_string.replace('</b>', '')
                    new_x_list.append(new_string)

            values = [new_x_list, flattened_y_list]

            genTableFile(header, values)

            app.layout = html.Div(children=[dcc.Graph(id='table', figure=table)
                , dcc.Graph(id='figure', figure=fig, style={'height': '40vh'}),
                                            ], style={'height': '40vh', 'width': '70vw'})
        else:
            app.layout = html.Div(children=[
                dcc.Graph(id='figure', figure=fig, style={'height': '90vh'}),
            ], style={'height': '70vh', 'width': '70vw'})

        return app, title, validDates


class Histogram(State):
    def __init__(self, reportGenerator, request, data):
        super(Histogram, self).__init__(reportGenerator, request, data)

    def findState(self):
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

        self.query_dictionary = {'Average visitors by time': 'avg_by_time', 'Average visitors by day': 'avg_by_day',
                                 'Total visitors by day': 'total_by_day', 'Total visitors by year': 'total_by_year'}

    # Get the date range for database querying
    def determineDateRange(self):
        self.date_subdict = self.inner_dict[2]
        self.from_time = self.date_subdict['from_time']
        self.to_time = self.date_subdict['to_time']

    def determineStyleSettings(self):
        self.style_dict = self.inner_dict[3]
        self.bar_color = self.style_dict['select_bar_color']
        self.autoscale = self.style_dict['autoscale']
        if self.autoscale == 'No':
            self.max_count = self.style_dict['max_count']
            self.increment_by = self.style_dict['increment_by']

    def determineLocationsToTrack(self):
        self.location_dict = self.inner_dict[4]
        self.location_list = self.location_dict['attendance_data']
        self.select_all = self.location_dict['select_all']
        if self.select_all:
            self.all_locations = True
        else:
            self.all_locations = False

    def generateReport(self):
        self.determineSelection()
        self.determineDateRange()
        self.determineStyleSettings()
        self.determineLocationsToTrack()

        conn = sqlite3.connect('vmc_tap.db');
        conn_results = []

        if self.all_locations:
            self.title = "Count of " + self.title + ", All Locations, from " + self.from_time.strftime(
                '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
        else:
            loc_str = ''
            for loc in self.location_list:
                if loc != self.location_list[-1]:
                    loc_str += loc + ', '
                else:
                    loc_str += loc

            self.title = "Count of " + self.title + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')

        custom_title = self.get_custom_title()
        if custom_title == '':
            title = self.title
        else:
            title = custom_title

        substr = "\""

        for i, location in enumerate(self.location_list):
            if i != (len(self.location_list) - 1):
                substr += location + '\' or location = \''
            else:
                substr += location

        substr += '"'

        self.conn_string_sql = eval(self.query_dictionary[self.selection] + ".get_query('" + self.from_time.strftime(
            '%Y-%m-%d') + "', '" + self.to_time.strftime(
            '%Y-%m-%d') + "', " + substr + ")")

        # conn_string_sql = "SELECT this_time, COUNT(this_time) FROM (SELECT LTRIM(SUBSTR(check_in_time,1,2),'0') || ' ' || SUBSTR(check_in_time,7,2) AS this_time, SUBSTR(check_in_time,1,2) + CASE(SUBSTR(check_in_time,7,2)) WHEN 'PM' THEN '12' ELSE '0' END AS sorting FROM visits) AS ctime GROUP BY this_time ORDER BY sorting;"
        # if self.selection == 'Average visitors by time':
        #   conn_string_sql = "SELECT cat_hours.hour_display, round(IFNULL(SUM(c_visits.visit_count), 0)/(julianday('" + self.to_time.strftime(
        #      '%Y-%m-%d') + "') - julianday('" + self.from_time.strftime(
        #     '%Y-%m-%d') + "')), 2) FROM cat_hours LEFT JOIN (SELECT LTRIM(SUBSTR(check_in_time,1,2),'0') || ' ' || SUBSTR(check_in_time,7,2) AS hour_display, 1 AS visit_count, check_in_date FROM visits WHERE (location = '" + substr + "') and check_in_date BETWEEN '" + self.from_time.strftime(
        #    '%Y-%m-%d') + "' AND '" + self.to_time.strftime(
        #   '%Y-%m-%d') + "') AS c_visits ON cat_hours.hour_display = c_visits.hour_display GROUP BY cat_hours.hour_display ORDER BY cat_hours.ordering;"
        # if self.selection == 'Average visitors by day':
        # Parts of this query was referenced from StackOverflow: https://stackoverflow.com/questions/4319302/format-date-as-day-of-week
        # conn_string_sql = "SELECT CASE cast (strftime('%w', check_in_date) AS INTEGER) WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday' WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday' ELSE 'Saturday' END AS Day, round(count(check_in_date)/(julianday('" + self.to_time.strftime(
        #       '%Y-%m-%d') + "') - julianday('" + self.from_time.strftime(
        #      '%Y-%m-%d') + "')), 2) FROM visits WHERE (location = '" + substr + "') and check_in_date BETWEEN '" + self.from_time.strftime(
        #     '%Y-%m-%d') + "' AND '" + self.to_time.strftime('%Y-%m-%d') + "' GROUP BY strftime('%w',check_in_date);"
        # if self.selection == 'Total visitors by day':
        #   conn_string_sql = "SELECT CASE cast (strftime('%w', check_in_date) AS INTEGER) WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday' WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday' ELSE 'Saturday' END AS Day, count(check_in_date) FROM visits WHERE (location = '" + substr + "') and check_in_date BETWEEN '" + self.from_time.strftime(
        #      '%Y-%m-%d') + "' AND '" + self.to_time.strftime('%Y-%m-%d') + "' GROUP BY strftime('%w',check_in_date);"
        # elif self.selection == 'Total visitors by year':
        #    conn_string_sql = "SELECT SUBSTR(check_in_date,1,4), COUNT(check_in_date) FROM visits WHERE (location = '" + substr + "') and check_in_date BETWEEN '" + self.from_time.strftime(
        #       '%Y-%m-%d') + "' AND '" + self.to_time.strftime('%Y-%m-%d') + "' GROUP BY SUBSTR(check_in_date,1,4);"

        # conn_string_sql = "select location, count(" + self.selection + ") from visits group by location;"

        print('conn_string_sql', self.conn_string_sql)
        #       print('conn.execute: ', conn.execute(conn_string_sql))

        for d in conn.execute(self.conn_string_sql):
            conn_results.append(d);

        conn.close()

        # Rotates 2D array to work w/ plotly
        conn_results_rotated = list(zip(*conn_results[::-1]));

        print('Conn results_rotated:', conn_results_rotated)

        app = DjangoDash('Graph')  # replaces dash.Dash

        # print('conn_results_rotated: ', conn_results_rotated)

        validDates = self.checkInvalidQuery(conn_results_rotated)

        if not validDates:
            x_axis = [1, 2, 3, 4, 5, 6, 7, 8]
            y_axis = [1, 2, 3, 4, 5, 6, 7, 8]
        # raise emptyList("List is empty")
        else:
            x_axis = conn_results_rotated[0]
            x_axis = x_axis[::-1]
            x_axis = list(x_axis)

            # x_axis = ['Time1', 'Time2', 'Time3', 'Time4']

            y_axis = conn_results_rotated[1]
            y_axis = y_axis[::-1]
            y_axis = list(y_axis)

            # y_axis = ["220", "100", "330", "410"]
            # for tuple in conn_results:
            #   x_axis.append(tuple[0])
            #  y_axis.append(tuple[1])

            print('x_axis: ', x_axis)
            print(y_axis)

        # If autoscaling is not enabled by the user, we need to set the max count of the y-axis
        if self.autoscale != 'Yes':
            layout = go.Layout(title=title, yaxis=dict(range=[0, self.max_count]))
        else:
            layout = Layout(title=title)

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
        # graph = [Bar(x=x_axis,y=y_axis)]
        # layout = Layout(title='Length of Visits',xaxis=dict(title='Length (min)'),yaxis=dict(title='# of Visits'))
        # fig = Figure(data=graph,layout=layout)
        # plot_div = plot(fig,output_type='div',show_link=False,link_text="")

        # Dash instance for includng a table
        if self.include_table == 'Yes' and validDates:
            header = ['Row Labels', 'Count of Location']
            x_list = list(x_axis)
            y_list = list(y_axis)
            values = [x_list, y_list]
            print('values: ', values)

            total = 0
            for count in y_axis:
                total += count

            x_list.append('<b>Grand Total</b>')
            y_list.append(total)
            table = go.Figure(data=[go.Table(header=dict(values=header), cells=dict(values=values))],
                              layout=Layout(title=title))
            table.update_layout(height=(200 + len(x_list) * 23))

            new_x_list = []

            for str in x_list:
                temp_new_string = str.replace('<b>', '')
                new_string = temp_new_string.replace('</b>', '')
                new_x_list.append(new_string)

            values = [new_x_list, y_list]

            genTableFile(header, values)

            app.layout = html.Div(children=[dcc.Graph(id='table', figure=table)
                , dcc.Graph(id='figure', figure=fig, style={'height': '40vh'}),
                                            ], style={'height': '40vh', 'width': '70vw'})
        else:
            app.layout = html.Div(children=[
                dcc.Graph(id='figure', figure=fig, style={'height': '90vh'}),
            ], style={'height': '70vh', 'width': '70vw'})

        print('validDates:', validDates)

        return app, title, validDates


class PieChart(State):
    def __init__(self, reportGenerator, request, data):
        super(PieChart, self).__init__(reportGenerator, request, data)

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

        self.query_dictionary = {'Benefit Chapter': 'benefit_chapter',
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

    def determineStyleSettings(self):
        self.style_dict = self.inner_dict[3]
        self.style_selection = self.style_dict['Data_units']

        if self.style_selection == 'Both percentages and count':
            self.textinfo = 'value+percent'
        elif self.style_selection == 'Percent of total':
            self.textinfo = 'percent'
        elif self.style_selection == 'Count':
            self.textinfo = 'value'

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

    def generateReport(self):
        self.determineSelection()
        self.determineDateRange()
        self.determineStyleSettings()
        self.determineLocationsToTrack()

        conn = sqlite3.connect('vmc_tap.db');
        conn_results = []

        if self.all_locations:
            self.title = "Count of " + self.title + ", All Locations, from " + self.from_time.strftime(
                '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
        else:
            loc_str = ''
            for loc in self.location_list:
                if loc != self.location_list[-1]:
                    loc_str += loc + ', '
                else:
                    loc_str += loc

            self.title = "Count of " + self.title + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')

        custom_title = self.get_custom_title()
        if custom_title == '':
            title = self.title
        else:
            title = custom_title

        substr = "\""

        for i, location in enumerate(self.location_list):
            if i != (len(self.location_list) - 1):
                substr += location + '\' or location = \''
            else:
                substr += location

        substr += '"'

        self.conn_string_sql = eval(self.query_dictionary[self.selection] + ".get_query('" + self.from_time.strftime(
            '%Y-%m-%d') + "', '" + self.to_time.strftime(
            '%Y-%m-%d') + "', " + substr + ")")
        print('location_list: ', self.location_list)

        # conn_string_sql = "select location, count(" + self.selection + ") from visits group by location;"

        print('conn_string_sql', self.conn_string_sql)
        #       print('conn.execute: ', conn.execute(conn_string_sql))

        for d in conn.execute(self.conn_string_sql):
            conn_results.append(d);

        conn.close()

        # Rotates 2D array to work w/ plotly
        conn_results_rotated = list(zip(*conn_results[::-1]));

        if conn_results_rotated:
            if 'Event' in conn_results_rotated[0] and self.use_custom_event_name == 'Yes':
                conn_results_rotated[0] = list(conn_results_rotated[0])
                i = conn_results_rotated[0].index('Event')
                custom_name = self.custom_event_name
                conn_results_rotated[0][i] = custom_name
                conn_results_rotated[0] = tuple(conn_results_rotated[0])

        print('Conn results_rotated:', conn_results_rotated)

        app = DjangoDash('Graph')  # replaces dash.Dash

        # print('conn_results_rotated: ', conn_results_rotated)

        validDates = self.checkInvalidQuery(conn_results_rotated)

        if conn_results_rotated == []:
            x_axis = [1, 2, 3, 4, 5, 6, 7, 8]
            y_axis = [1, 2, 3, 4, 5, 6, 7, 8]
        # raise emptyList("List is empty")
        else:
            x_axis = conn_results_rotated[0]
            y_axis = conn_results_rotated[1]
            x_axis = x_axis[::-1]
            y_axis = y_axis[::-1]
            # for tuple in conn_results:
            #    x_axis.append(tuple[0])
            #   y_axis.append(tuple[1])

            print('x_axis: ', x_axis)
            print(y_axis)

        layout = Layout(title=title)
        fig = go.Figure(data=[go.Pie(labels=x_axis, values=y_axis, textinfo=self.textinfo)], layout=layout)

        # graph = [Bar(x=x_axis,y=y_axis)]
        # layout = Layout(title='Length of Visits',xaxis=dict(title='Length (min)'),yaxis=dict(title='# of Visits'))
        # fig = Figure(data=graph,layout=layout)
        # plot_div = plot(fig,output_type='div',show_link=False,link_text="")

        # Dash instance for includng a table
        if self.include_table == 'Yes' and validDates:
            header = ['Row Labels', 'Count of Location']
            x_list = list(x_axis)
            y_list = list(y_axis)
            values = [x_list, y_list]
            print('values: ', values)

            total = 0
            for count in y_axis:
                total += count

            x_list.append('<b>Grand Total</b>')
            y_list.append(total)
            table = go.Figure(data=[go.Table(header=dict(values=header), cells=dict(values=values))],
                              layout=Layout(title=title))

            app.layout = html.Div(children=[dcc.Graph(id='table', figure=table)
                , dcc.Graph(id='figure', figure=fig, style={'height': '80vh', 'width': '80vw'}),
                                            ], style={'height': '40vh', 'width': '70vw'})
            table.update_layout(height=(200 + len(x_list) * 23))

            new_x_list = []

            for str in x_list:
                temp_new_string = str.replace('<b>', '')
                new_string = temp_new_string.replace('</b>', '')
                new_x_list.append(new_string)

            values = [new_x_list, y_list]

            genTableFile(header, values)
        else:
            app.layout = html.Div(children=[
                dcc.Graph(id='figure', figure=fig, style={'height': '90vh'}),
            ], style={'height': '70vh', 'width': '70vw'})

        return app, title, validDates


# Select count from visits where date >= from_date and date <= to_date group by location

class IndividualStatistic(State):
    def __init__(self, reportGenerator, request, data):
        super(IndividualStatistic, self).__init__(reportGenerator, request, data)

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

        # Convert selection into query '*' for SQL
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

        self.query_dictionary = {'Benefit Chapter': 'benefit_chapter',
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

    def determineStyleSettings(self):
        self.style_dict = self.inner_dict[3]
        self.header_font_color = self.style_dict['header_font_color']
        self.statistic_font_color = self.style_dict['statistic_font_color']
        self.header_font_size = self.style_dict['header_font_size']
        self.statistic_font_size = self.style_dict['statistic_font_size']

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

    def generateReport(self):
        self.determineSelection()
        self.determineDateRange()
        self.determineStyleSettings()
        self.determineLocationsToTrack()

        conn = sqlite3.connect('vmc_tap.db');
        conn_results = []

        if self.all_locations:
            self.title = "Count of " + self.title + ", All Locations, from " + self.from_time.strftime(
                '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
        else:
            loc_str = ''
            for loc in self.location_list:
                if loc != self.location_list[-1]:
                    loc_str += loc + ', '
                else:
                    loc_str += loc

            self.title = "Count of " + self.title + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')

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

        custom_title = self.get_custom_title()
        if custom_title == '':
            title = new_title
        else:
            title = custom_title

        # if self.subselection == 'Total Count':
        #   conn_string_sql = "select " + self.group_by + ", count(" + self.selection + ") from visits where (location = \'" + substr + "\') and check_in_date >= \'" + self.from_time.strftime(
        #      '%Y-%m-%d') + "\' and check_in_date <= \'" + self.to_time.strftime(
        #     '%Y-%m-%d') + "\' group by " + self.group_by + ";"
        # print('location_list: ', self.location_list)
        # elif self.subselection == 'Daily average':
        # conn_string_sql = "select major, avg(count(*)) from (select check_in_date, count(*) from visits) group by major;"
        #   conn_string_sql = "SELECT " + self.group_by + ", ROUND(COUNT(" + self.group_by + ") / (julianday('" + self.to_time.strftime(
        #      '%Y-%m-%d') + "') - julianday('" + self.from_time.strftime(
        #     '%Y-%m-%d') + "')), 2) FROM visits WHERE check_in_date BETWEEN '" + self.from_time.strftime(
        #    '%Y-%m-%d') + "' AND '" + self.to_time.strftime('%Y-%m-%d') + "' GROUP BY " + self.group_by + ";"
        # elif self.subselection == 'Monthly average':
        #   conn_string_sql = "SELECT " + self.group_by + ", ROUND(COUNT(" + self.group_by + ") / (strftime('%m','" + self.to_time.strftime(
        #      '%Y-%m-%d') + "') - strftime('%m', '" + self.from_time.strftime(
        #     '%Y-%m-%d') + "')), 2) FROM visits WHERE check_in_date BETWEEN '" + self.from_time.strftime(
        #    '%Y-%m-%d') + "' AND '" + self.to_time.strftime('%Y-%m-%d') + "' GROUP BY " + self.group_by + ";"
        # elif self.subselection == 'Yearly average':
        #   conn_string_sql = "SELECT " + self.group_by + ", ROUND(COUNT(" + self.group_by + ") / (strftime('%Y','" + self.to_time.strftime(
        #      '%Y-%m-%d') + "') - strftime('%Y', '" + self.from_time.strftime(
        #     '%Y-%m-%d') + "')), 2) FROM visits WHERE check_in_date BETWEEN '" + self.from_time.strftime(
        #    '%Y-%m-%d') + "' AND '" + self.to_time.strftime('%Y-%m-%d') + "' GROUP BY " + self.group_by + ";"

        substr = "\""

        for i, location in enumerate(self.location_list):
            if i != (len(self.location_list) - 1):
                substr += location + '\' or location = \''
            else:
                substr += location

        substr += '"'

        if self.subselection == 'Total Count':
            self.conn_string_sql = eval(
                self.query_dictionary[self.selection] + ".get_query('" + self.from_time.strftime(
                    '%Y-%m-%d') + "', '" + self.to_time.strftime(
                    '%Y-%m-%d') + "', " + substr + ")")
        elif self.subselection == 'Daily average':
            self.conn_string_sql = eval(
                "ind_daily_avg.get_query('" + self.query_dictionary[self.selection] + "', '" + self.from_time.strftime(
                    '%Y-%m-%d') + "', '" + self.to_time.strftime(
                    '%Y-%m-%d') + "', " + substr + ")")
        elif self.subselection == 'Monthly average':
            self.conn_string_sql = eval(
                "ind_monthly_avg.get_query('" + self.query_dictionary[
                    self.selection] + "', '" + self.from_time.strftime(
                    '%Y-%m-%d') + "', '" + self.to_time.strftime(
                    '%Y-%m-%d') + "', " + substr + ")")
        elif self.subselection == 'Yearly average':
            self.conn_string_sql = eval(
                "ind_yearly_avg.get_query('" + self.query_dictionary[
                    self.selection] + "', '" + self.from_time.strftime(
                    '%Y-%m-%d') + "', '" + self.to_time.strftime(
                    '%Y-%m-%d') + "', " + substr + ")")

        print('location_list: ', self.location_list)

        # conn_string_sql = "select location, count(" + self.selection + ") from visits group by location;"

        print('conn_string_sql', self.conn_string_sql)
        #       print('conn.execute: ', conn.execute(conn_string_sql))

        for d in conn.execute(self.conn_string_sql):
            conn_results.append(d);

        conn.close()

        # Rotates 2D array to work w/ plotly
        conn_results_rotated = list(zip(*conn_results[::-1]))

        if conn_results_rotated:
            if 'Event' in conn_results_rotated[0] and self.use_custom_event_name == 'Yes':
                conn_results_rotated[0] = list(conn_results_rotated[0])
                i = conn_results_rotated[0].index('Event')
                custom_name = self.custom_event_name
                conn_results_rotated[0][i] = custom_name
                conn_results_rotated[0] = tuple(conn_results_rotated[0])

        print('Conn results_rotated:', conn_results_rotated)

        app = DjangoDash('Graph')  # replaces dash.Dash

        # print('conn_results_rotated: ', conn_results_rotated)

        validDates = self.checkInvalidQuery(conn_results_rotated)

        if conn_results_rotated == []:
            x_axis = [1, 2, 3, 4, 5, 6, 7, 8]
            y_axis = [1, 2, 3, 4, 5, 6, 7, 8]
        # raise emptyList("List is empty")
        else:
            x_axis = conn_results_rotated[0]
            y_axis = conn_results_rotated[1]
            x_axis = x_axis[::-1]
            y_axis = y_axis[::-1]
            # for tuple in conn_results:
            #    x_axis.append(tuple[0])
            #   y_axis.append(tuple[1])

        header = ['Row Labels', 'Count of Location']
        x_list = list(x_axis)
        y_list = list(y_axis)
        values = [x_list, y_list]
        print('values: ', values)

        total = 0
        for count in y_axis:
            total += count

        x_list.append('<b>Grand Total</b>')
        y_list.append(total)

        layout = Layout(title=title)
        table = go.Figure(data=[go.Table(header=dict(values=header, height=int(self.header_font_size) * 3,
                                                     font=dict(color=self.header_font_color,
                                                               size=int(self.header_font_size))),
                                         cells=dict(values=values, height=int(self.statistic_font_size) * 3,
                                                    font=dict(color=self.statistic_font_color,
                                                              size=int(self.statistic_font_size))))],
                          layout=Layout(title=title))

        table.update_layout(height=(200 + len(x_list) * 23))

        new_x_list = []

        if validDates:
            for str in x_list:
                temp_new_string = str.replace('<b>', '')
                new_string = temp_new_string.replace('</b>', '')
                new_x_list.append(new_string)

        values = [new_x_list, y_list]

        genTableFile(header, values)

        app.layout = html.Div(children=[dcc.Graph(id='table', figure=table, style={'height': '70vh'})
                                        ], style={'height': '80vh', 'width': '70vw'})

        # graph = [Bar(x=x_axis,y=y_axis)]
        # layout = Layout(title='Length of Visits',xaxis=dict(title='Length (min)'),yaxis=dict(title='# of Visits'))
        # fig = Figure(data=graph,layout=layout)
        # plot_div = plot(fig,output_type='div',show_link=False,link_text="")
        return app, title, validDates


class ScatterPlot(State):
    def __init__(self, reportGenerator, request, data):
        super(ScatterPlot, self).__init__(reportGenerator, request, data)

    def findState(self):
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

    def generateReport(self):
        self.determineSelection()
        self.determineDateRange()
        self.determineStyleSettings()
        self.determineLocationsToTrack()

        conn = sqlite3.connect('vmc_tap.db')
        conn_results = []

        if self.all_locations:
            if self.report_type == 'Count visits over time':
                self.title = "Count of " + self.title + ", all Locations from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
            elif self.report_type == 'Compare GPA against demographics':
                self.title = self.gpa_to_compare + " by " + self.category + ", all Locations, from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
        else:
            loc_str = ''
            for loc in self.location_list:
                if loc != self.location_list[-1]:
                    loc_str += loc + ', '
                else:
                    loc_str += loc

            if self.report_type == 'Count visits over time':
                self.title = "Count of " + self.title + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')
            elif self.report_type == 'Compare GPA against demographics':
                self.title = self.gpa_to_compare + " by " + self.category + " at location(s):" + loc_str + " from " + self.from_time.strftime(
                    '%m/%d/%Y') + " to " + self.to_time.strftime('%m/%d/%Y')

        custom_title = self.get_custom_title()
        if custom_title == '':
            title = self.title
        else:
            title = custom_title

        substr = "\""

        for i, location in enumerate(self.location_list):
            if i != (len(self.location_list) - 1):
                substr += location + '\' or location = \''
            else:
                substr += location

        substr += '"'

        if self.report_type == 'Count visits over time':
            self.conn_string_sql = eval(
                self.query_dictionary[self.selection] + ".get_query('" + self.from_time.strftime(
                    '%Y-%m-%d') + "', '" + self.to_time.strftime(
                    '%Y-%m-%d') + "', " + substr + ")")
        elif self.report_type == 'Compare GPA against demographics':
            self.conn_string_sql = eval(
                self.query_dictionary[self.category] + "_gpa.get_query('" + self.gpa_dictionary[
                    self.gpa_to_compare] + "', '" + self.from_time.strftime(

                    '%Y-%m-%d') + "', '" + self.to_time.strftime(
                    '%Y-%m-%d') + "', " + substr + ")")
        print('location_list: ', self.location_list)

        # conn_string_sql = "select location, count(" + self.selection + ") from visits group by location;"

        print('conn_string_sql', self.conn_string_sql)
        #       print('conn.execute: ', conn.execute(conn_string_sql))

        for d in conn.execute(self.conn_string_sql):
            conn_results.append(d);

        conn.close()

        # Rotates 2D array to work w/ plotly
        conn_results_rotated = list(zip(*conn_results[::-1]))

        if conn_results_rotated:
            if 'Event' in conn_results_rotated[0] and self.use_custom_event_name == 'Yes':
                conn_results_rotated[0] = list(conn_results_rotated[0])
                i = conn_results_rotated[0].index('Event')
                custom_name = self.custom_event_name
                conn_results_rotated[0][i] = custom_name
                conn_results_rotated[0] = tuple(conn_results_rotated[0])

        print('Conn results_rotated:', conn_results_rotated)

        app = DjangoDash('Graph')  # replaces dash.Dash

        # print('conn_results_rotated: ', conn_results_rotated)

        validDates = self.checkInvalidQuery(conn_results_rotated)

        if conn_results_rotated == []:
            x_axis = [1, 2, 3, 4, 5, 6, 7, 8]
            y_axis = [1, 2, 3, 4, 5, 6, 7, 8]
        # raise emptyList("List is empty")
        else:
            x_axis = conn_results_rotated[0]
            y_axis = conn_results_rotated[1]
            x_axis = x_axis[::-1]
            y_axis = y_axis[::-1]
            # for tuple in conn_results:
            #    x_axis.append(tuple[0])
            #   y_axis.append(tuple[1])

            print('x_axis: ', x_axis)

        if self.autoscale != 'Yes':
            layout = go.Layout(title=title, yaxis=dict(range=[0, self.max_count]))
        else:
            layout = Layout(title=title)

        fig = go.Figure(
            data=[go.Scatter(x=x_axis, y=y_axis, mode=self.mode, marker=dict(color=self.bar_color.lower()))],
            layout=layout)

        if self.autoscale != 'Yes':
            fig.update_yaxes(dtick=self.increment_by)
        # graph = [Bar(x=x_axis,y=y_axis)]
        # layout = Layout(title='Length of Visits',xaxis=dict(title='Length (min)'),yaxis=dict(title='# of Visits'))
        # fig = Figure(data=graph,layout=layout)
        # plot_div = plot(fig,output_type='div',show_link=False,link_text="")

        # Dash instance for includng a table
        if self.include_table == 'Yes' and validDates:
            header = ['Row Labels', 'Count of Location']
            x_list = list(x_axis)
            y_list = list(y_axis)
            values = [x_list, y_list]

            if self.report_type == 'Count visits over time':
                total = 0
                for count in y_axis:
                    total += count

                x_list.append('<b>Grand Total</b>')
                y_list.append(total)
            elif self.report_type == 'Compare GPA against demographics':
                total_values = len(y_list)
                total = 0
                for count in y_axis:
                    total += count
                x_list.append('<b>Total Average<b>')
                total /= total_values
                y_list.append(round(total, 2))
            table = go.Figure(data=[go.Table(header=dict(values=header), cells=dict(values=values))],
                              layout=Layout(title=title))
            table.update_layout(height=(200 + len(x_list) * 23))

            app.layout = html.Div(children=[dcc.Graph(id='table', figure=table)
                , dcc.Graph(id='figure', figure=fig, style={'height': '80vh', 'width': '80vw'}),
                                            ], style={'height': '40vh', 'width': '70vw'})

            new_x_list = []

            for str in x_list:
                temp_new_string = str.replace('<b>', '')
                new_string = temp_new_string.replace('</b>', '')
                new_x_list.append(new_string)

            values = [new_x_list, y_list]

            genTableFile(header, values)

        else:
            app.layout = html.Div(children=[
                dcc.Graph(id='figure', figure=fig, style={'height': '90vh'}),
            ], style={'height': '70vh', 'width': '70vw'})

        return app, title, validDates


def getReport(request):
    data = pageViews.preset_storage
    inner_dict = data['form_data']
    graph_type_dict = inner_dict[0]
    graph_type = graph_type_dict['graphType']
    reportGenerator = ReportGenerator(request, data)
    app, title, valid_dates = reportGenerator.generateReport()

    if valid_dates:
        return render(request, 'visualizations/getReport.html', context={'graphTitle': title})
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
            if valid_dates:
                return render(request, 'visualizations/getReport.html', context={'graphTitle': title})
            else:
                form = TimeFrame()
                return render(request, 'visualizations/queryCorrection.html', context={'form': form})
        else:
            return render(request, 'visualizations/queryCorrection.html', context={'form': form})
    else:
        form = TimeFrame()
        return render(request, 'visualizations/queryCorrection.html', context={'form': form})


def dateQueryCorrection(data, new_from_time, new_to_time):
    inner_dict = data['form_data']
    date_subdict = inner_dict[2]
    date_subdict['from_time'] = new_from_time
    date_subdict['to_time'] = new_to_time

    return data


# Convert bar graph preset data back into dictionary format to prepare send it to the report generator
def getBarGraphPreset(presetModel, from_time, to_time):
    from_time = datetime.strptime(from_time, '%m-%d-%Y')
    to_time = datetime.strptime(to_time, '%m-%d-%Y')
    report_data = {}
    report_data['form_data'] = []
    inner_list = report_data['form_data']
    inner_list.append({'graphType': 'Bar Graph', 'title': presetModel.title})
    inner_list.append({'selection': presetModel.selection, 'include_table': presetModel.include_table})
    inner_list.append({'from_time': from_time, 'to_time': to_time})
    if presetModel.autoscale == 'Yes':
        inner_list.append({'select_bar_color': presetModel.select_bar_color, 'autoscale': presetModel.autoscale,
                           'show_multiple_bars_by_location': presetModel.multiple_bars, 'max_count': None,
                           'increment_by': None})
    else:
        inner_list.append({'select_bar_color': presetModel.select_bar_color, 'autoscale': presetModel.autoscale,
                           'show_multiple_bars_by_location': presetModel.multiple_bars,
                           'max_count': presetModel.max_count, 'increment_by': presetModel.increment_by})

    inner_list.append({'attendance_data': presetModel.locations.split(','), 'select_all': presetModel.select_all})

    return report_data


# Convert histogram preset data back into dictionary format to prepare send it to the report generator
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

    inner_list.append({'attendance_data': presetModel.locations.split(','), 'select_all': presetModel.select_all})

    return report_data


def getLineScatterPreset(presetModel, from_time, to_time):
    from_time = datetime.strptime(from_time, '%m-%d-%Y')
    to_time = datetime.strptime(to_time, '%m-%d-%Y')
    report_data = {}
    report_data['form_data'] = []
    inner_list = report_data['form_data']
    inner_list.append({'graphType': 'Line and/or Scatter', 'title': presetModel.title})
    inner_list.append({'selection': presetModel.selection, 'include_table': presetModel.include_table})
    inner_list.append({'from_time': from_time, 'to_time': to_time})
    if presetModel.autoscale == 'Yes':
        inner_list.append({'autoscale': presetModel.autoscale, 'max_count': None,
                           'increment_by': None, 'select_dot_color': presetModel.dot_color,
                           'display_as': presetModel.display_options})
    else:
        inner_list.append({'autoscale': presetModel.autoscale, 'max_count': presetModel.max_count,
                           'increment_by': presetModel.increment_by, 'select_dot_color': presetModel.dot_color,
                           'display_as': presetModel.display_options})

    inner_list.append({'attendance_data': presetModel.locations.split(','), 'select_all': presetModel.select_all})

    return report_data


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
    inner_list.append({'attendance_data': presetModel.locations.split(','), 'select_all': presetModel.select_all})

    return report_data


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

    inner_list.append({'attendance_data': presetModel.locations.split(','), 'select_all': presetModel.select_all})

    return report_data


def presetReport(request, preset_name, from_time, to_time):
    preset = ReportPresets.objects.get(pk=preset_name)
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

    app, title, valid_dates = reportGenerator.generateReport()

    if valid_dates:
        return render(request, 'visualizations/getReport.html', context={'graphTitle': title})
    else:
        form = TimeFrame()
        pageViews.preset_storage = data_dict
        return render(request, 'visualizations/queryCorrection.html', context={'form': form})


def callback_size(dropdown_color, dropdown_size):
    return "The chosen T-shirt is a %s %s one." % (dropdown_size,
                                                   dropdown_color)


def plotly(request):
    demographics = ['WHITE', 'BLACK', 'HISPA', 'ASIAN', 'UNKWN']
    average_visits = [random.uniform(1.5, 6) for x in demographics]
    graph = [Bar(x=demographics, y=average_visits)]
    layout = Layout(title='Average # of Visits by Ethnicity', xaxis=dict(title='Ethnicity'),
                    yaxis=dict(title='Average # of Visits'))
    fig = Figure(data=graph, layout=layout)
    plot_div = plot(fig, output_type='div', show_link=False, link_text="")
    return render(request, "visualizations/plotly.html", context={'plot_div': plot_div})


# Create your views here.
def exampleGraph(request):
    app = DjangoDash('SimpleExample')  # replaces dash.Dash

    conn = sqlite3.connect('vmc_tap.db');
    conn_results = [];

    conn_string_sql = "select round(check_in_duration/5)*5, count(round(check_in_duration/5)*5) from visits group by round(check_in_duration/5)*5;";

    for d in conn.execute(conn_string_sql):
        conn_results.append(d);

    # Rotates 2D array to work w/ plotly
    conn_results_rotated = list(zip(*conn_results[::-1]));

    if conn_results_rotated == []:
        x_axis = [1, 2, 3, 4, 5, 6, 7, 8]
        y_axis = [1, 2, 3, 4, 5, 6, 7, 8]
    # raise emptyList("List is empty")
    else:
        x_axis = conn_results_rotated[0];
        y_axis = conn_results_rotated[1];

    fig = go.Figure(data=[go.Bar(x=x_axis, y=y_axis)])
    # graph = [Bar(x=x_axis,y=y_axis)]
    # layout = Layout(title='Length of Visits',xaxis=dict(title='Length (min)'),yaxis=dict(title='# of Visits'))
    # fig = Figure(data=graph,layout=layout)
    # plot_div = plot(fig,output_type='div',show_link=False,link_text="")

    app.layout = html.Div(children=[
        dcc.Graph(id='figure', figure=fig),
    ], style={'height': '100vh'})

    return render(request, 'visualizations/exampleGraph.html')


def genTableFile(header, values):
    rows = zip(values[0], values[1])
    with open(os.path.join(os.getcwd(), 'table.csv'), 'w+', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(header)
        for value in rows:
            csvwriter.writerow(value)
        csvfile.close()


def downloadFile(request):
    path = os.path.join(os.getcwd(), 'table.csv')

    file = open(path, 'r')
    response = HttpResponse(file, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="%s"' % 'table.csv'

    os.remove(path)

    return response
