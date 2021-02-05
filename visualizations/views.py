from django.shortcuts import render
from plotly.offline import plot
from plotly.graph_objs import Bar
from plotly.graph_objs import Figure
from plotly.graph_objs import Layout
import random
from pages import views as pageViews
import sqlite3;

import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objects as go

from django_plotly_dash import DjangoDash


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

    def setState(self, state):
        self.state = state

    def generateReport(self):
        app, title = self.state.generateReport()
        return app, title


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


class BarGraph(State):
    def __init__(self, reportGenerator, request, data):
        super(BarGraph, self).__init__(reportGenerator, request, data)

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
        self.selection = self.selection_dict['selection']
        self.title = self.selection
        self.include_table = self.selection_dict['include_table']

        # Convert selection into query '*' for SQL
        if self.selection == 'Total Usage by Location':
            self.selection = '*'
            self.group_by = 'location'
        elif self.selection == 'Usage by Date':
            self.selection = '*'
            self.group_by = 'check_in_date'
        elif self.selection == 'Classification':
            self.group_by = 'classification'
        elif self.selection == 'Major':
            self.group_by = 'major'
        elif self.selection == 'Services':
            self.group_by = 'services'

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

    def generateReport(self):
        self.determineSelection()
        self.determineDateRange()
        self.determineStyleSettings()
        self.determineLocationsToTrack()

        conn = sqlite3.connect('vmc_tap.db');
        conn_results = []

        title = self.title

        substr = ''

        for i, location in enumerate(self.location_list):
            if i != (len(self.location_list) - 1):
                substr += location + '\' or location = \''
            else:
                substr += location

        conn_string_sql = "select " + self.group_by + ", count(" + self.selection + ") from visits where (location = \'" + substr + "\') and check_in_date >= \'" + self.from_time.strftime(
            '%Y-%m-%d') + "\' and check_in_date <= \'" + self.to_time.strftime(
            '%Y-%m-%d') + "\' group by " + self.group_by + ";"
        print('location_list: ', self.location_list)

        # conn_string_sql = "select location, count(" + self.selection + ") from visits group by location;"

        print('conn_string_sql', conn_string_sql)
        #       print('conn.execute: ', conn.execute(conn_string_sql))

        for d in conn.execute(conn_string_sql):
            conn_results.append(d);

        conn.close()

        # Rotates 2D array to work w/ plotly
        conn_results_rotated = list(zip(*conn_results[::-1]));

        print('Conn results_rotated:', conn_results_rotated)

        app = DjangoDash('Graph')  # replaces dash.Dash

        # print('conn_results_rotated: ', conn_results_rotated)

        if conn_results_rotated == []:
            x_axis = [1, 2, 3, 4, 5, 6, 7, 8]
            y_axis = [1, 2, 3, 4, 5, 6, 7, 8]
        # raise emptyList("List is empty")
        else:
            x_axis = conn_results_rotated[0];
            y_axis = conn_results_rotated[1];
            # for tuple in conn_results:
            #    x_axis.append(tuple[0])
            #   y_axis.append(tuple[1])

            print('x_axis: ', x_axis)
            print(y_axis)

        # If autoscaling is not enabled by the user, we need to set the max count of the y-axis
        if self.autoscale != 'Yes':
            layout = go.Layout(title=title, yaxis=dict(range=[0, self.max_count]))
        else:
            layout = Layout(title=title)

        fig = go.Figure(data=[go.Bar(x=x_axis, y=y_axis, marker=dict(color=self.bar_color.lower()))], layout=layout)

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
            x_list = list(x_axis)
            y_list = list(y_axis)
            values = [x_list, y_list]
            print('values: ', values)

            total = 0
            for count in y_axis:
                total += count

            x_list.append('<b>Grand Total</b>')
            y_list.append(total)
            table = go.Figure(data=[go.Table(header=dict(values=header), cells=dict(values=values))])

            app.layout = html.Div(children=[dcc.Graph(id='table', figure=table)
                , dcc.Graph(id='figure', figure=fig, style={'height': '40vh'}),
                                            ], style={'height': '40vh', 'width': '70vw'})
        else:
            app.layout = html.Div(children=[
                dcc.Graph(id='figure', figure=fig, style={'height': '90vh'}),
            ], style={'height': '70vh', 'width': '70vw'})

        return app, title


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

        # Convert selection into query '*' for SQL
        if self.selection == 'Total Usage by Location':
            self.selection = '*'
            self.group_by = 'location'
        elif self.selection == 'Usage by Date':
            self.selection = '*'
            self.group_by = 'check_in_date'
        elif self.selection == 'Classification':
            self.group_by = 'classification'
        elif self.selection == 'Major':
            self.group_by = 'major'
        elif self.selection == 'Services':
            self.group_by = 'services'

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

    def generateReport(self):
        self.determineSelection()
        self.determineDateRange()
        self.determineStyleSettings()
        self.determineLocationsToTrack()

        conn = sqlite3.connect('vmc_tap.db');
        conn_results = []

        title = self.title

        substr = ''

        for i, location in enumerate(self.location_list):
            if i != (len(self.location_list) - 1):
                substr += location + '\' or location = \''
            else:
                substr += location

        conn_string_sql = "select " + self.group_by + ", count(" + self.selection + ") from visits where (location = \'" + substr + "\') and check_in_date >= \'" + self.from_time.strftime(
            '%Y-%m-%d') + "\' and check_in_date <= \'" + self.to_time.strftime(
            '%Y-%m-%d') + "\' group by " + self.group_by + ";"
        print('location_list: ', self.location_list)

        # conn_string_sql = "select location, count(" + self.selection + ") from visits group by location;"

        print('conn_string_sql', conn_string_sql)
        #       print('conn.execute: ', conn.execute(conn_string_sql))

        for d in conn.execute(conn_string_sql):
            conn_results.append(d);

        conn.close()

        # Rotates 2D array to work w/ plotly
        conn_results_rotated = list(zip(*conn_results[::-1]));

        print('Conn results_rotated:', conn_results_rotated)

        app = DjangoDash('Graph')  # replaces dash.Dash

        # print('conn_results_rotated: ', conn_results_rotated)

        if conn_results_rotated == []:
            x_axis = [1, 2, 3, 4, 5, 6, 7, 8]
            y_axis = [1, 2, 3, 4, 5, 6, 7, 8]
        # raise emptyList("List is empty")
        else:
            x_axis = conn_results_rotated[0];
            y_axis = conn_results_rotated[1];
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
        if self.include_table == 'Yes':
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
            table = go.Figure(data=[go.Table(header=dict(values=header), cells=dict(values=values))])

            app.layout = html.Div(children=[dcc.Graph(id='table', figure=table)
                , dcc.Graph(id='figure', figure=fig, style={'height': '80vh', 'width': '80vw'}),
                                            ], style={'height': '40vh', 'width': '70vw'})
        else:
            app.layout = html.Div(children=[
                dcc.Graph(id='figure', figure=fig, style={'height': '90vh'}),
            ], style={'height': '70vh', 'width': '70vw'})

        return app, title
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
            self.selection = '*'
            self.group_by = 'location'
        elif self.selection == 'Usage by Date':
            self.selection = '*'
            self.group_by = 'check_in_date'
        elif self.selection == 'Classification':
            self.group_by = 'classification'
        elif self.selection == 'Major':
            self.group_by = 'major'
        elif self.selection == 'Services':
            self.group_by = 'services'

    # Get the date range for database querying
    def determineDateRange(self):
        self.date_subdict = self.inner_dict[2]
        self.from_time = self.date_subdict['from_time']
        self.to_time = self.date_subdict['to_time']

    def determineStyleSettings(self):
        self.style_dict = self.inner_dict[3]
        self.label_font_color = self.style_dict['label_font_color']
        self.statistic_font_color = self.style_dict['statistic_font_color']
        self.label_font_size = self.style_dict['label_font_size']
        self.statistic_font_size = self.style_dict['statistic_font_size']


    def determineLocationsToTrack(self):
        self.location_dict = self.inner_dict[4]
        self.location_list = self.location_dict['attendance_data']

    def generateReport(self):
        self.determineSelection()
        self.determineDateRange()
        self.determineStyleSettings()
        self.determineLocationsToTrack()

        conn = sqlite3.connect('vmc_tap.db');
        conn_results = []

        if self.subselection == 'Total Count':
            title = 'Total count of visitors from ' + self.from_time.strftime('%m/%d/%y') + ' to ' + self.to_time.strftime('%m/%d/%y')
        elif self.subselection == 'Daily average':
            title = 'Daily average visitors from ' + self.from_time.strftime('%m/%d/%d') + ' to ' + self.to_time.strftime('%m/%d/%y')
        elif self.subselection == 'Monthly average':
            title = 'Monthly average visitors from ' + self.from_time.strftime(
                '%m/%d/%d') + ' to ' + self.to_time.strftime('%m/%d/%y')
        elif self.subselection == 'Yearly average':
            title = 'Yearly average visitors from ' + self.from_time.strftime(

            )

        # The max size of a location list is 2. If this is true, then show "all locations in the title"
        if len(self.location_list) == 2:
            title2 = ' Locations: All'
        else:
            title2 = ' Locations: '
            for location in self.location_list:
                title2 += location + ' '

        title += '\n' + title2

        for i, location in enumerate(self.location_list):
            if i != (len(self.location_list) - 1):
                substr += location + '\' or location = \''
            else:
                substr += location

        conn_string_sql = "select " + self.group_by + ", count(" + self.selection + ") from visits where (location = \'" + substr + "\') and check_in_date >= \'" + self.from_time.strftime(
            '%Y-%m-%d') + "\' and check_in_date <= \'" + self.to_time.strftime(
            '%Y-%m-%d') + "\' group by " + self.group_by + ";"
        print('location_list: ', self.location_list)

        # conn_string_sql = "select location, count(" + self.selection + ") from visits group by location;"

        print('conn_string_sql', conn_string_sql)
        #       print('conn.execute: ', conn.execute(conn_string_sql))

        for d in conn.execute(conn_string_sql):
            conn_results.append(d);

        conn.close()

        # Rotates 2D array to work w/ plotly
        conn_results_rotated = list(zip(*conn_results[::-1]));

        print('Conn results_rotated:', conn_results_rotated)

        app = DjangoDash('Graph')  # replaces dash.Dash

        # print('conn_results_rotated: ', conn_results_rotated)

        if conn_results_rotated == []:
            x_axis = [1, 2, 3, 4, 5, 6, 7, 8]
            y_axis = [1, 2, 3, 4, 5, 6, 7, 8]
        # raise emptyList("List is empty")
        else:
            x_axis = conn_results_rotated[0];
            y_axis = conn_results_rotated[1];
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
        table = go.Figure(data=[go.Table(header=dict(values=header), cells=dict(values=values))], layout=layout)

        app.layout = html.Div(children=[dcc.Graph(id='table', figure=table)
                                        ], style={'height': '40vh', 'width': '70vw'})


        # graph = [Bar(x=x_axis,y=y_axis)]
        # layout = Layout(title='Length of Visits',xaxis=dict(title='Length (min)'),yaxis=dict(title='# of Visits'))
        # fig = Figure(data=graph,layout=layout)
        # plot_div = plot(fig,output_type='div',show_link=False,link_text="")
        return app, title

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

        # Convert selection into query '*' for SQL
        if self.selection == 'Total Usage by Location':
            self.selection = '*'
            self.group_by = 'location'
        elif self.selection == 'Usage by Date':
            self.selection = '*'
            self.group_by = 'check_in_date'
        elif self.selection == 'Classification':
            self.group_by = 'classification'
        elif self.selection == 'Major':
            self.group_by = 'major'
        elif self.selection == 'Services':
            self.group_by = 'services'

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

    def generateReport(self):
        self.determineSelection()
        self.determineDateRange()
        self.determineStyleSettings()
        self.determineLocationsToTrack()

        conn = sqlite3.connect('vmc_tap.db');
        conn_results = []

        title = self.title

        substr = ''

        for i, location in enumerate(self.location_list):
            if i != (len(self.location_list) - 1):
                substr += location + '\' or location = \''
            else:
                substr += location

        conn_string_sql = "select " + self.group_by + ", count(" + self.selection + ") from visits where (location = \'" + substr + "\') and check_in_date >= \'" + self.from_time.strftime(
            '%Y-%m-%d') + "\' and check_in_date <= \'" + self.to_time.strftime(
            '%Y-%m-%d') + "\' group by " + self.group_by + ";"
        print('location_list: ', self.location_list)

        # conn_string_sql = "select location, count(" + self.selection + ") from visits group by location;"

        print('conn_string_sql', conn_string_sql)
        #       print('conn.execute: ', conn.execute(conn_string_sql))

        for d in conn.execute(conn_string_sql):
            conn_results.append(d);

        conn.close()

        # Rotates 2D array to work w/ plotly
        conn_results_rotated = list(zip(*conn_results[::-1]));

        print('Conn results_rotated:', conn_results_rotated)

        app = DjangoDash('Graph')  # replaces dash.Dash

        # print('conn_results_rotated: ', conn_results_rotated)

        if conn_results_rotated == []:
            x_axis = [1, 2, 3, 4, 5, 6, 7, 8]
            y_axis = [1, 2, 3, 4, 5, 6, 7, 8]
        # raise emptyList("List is empty")
        else:
            x_axis = conn_results_rotated[0];
            y_axis = conn_results_rotated[1];
            # for tuple in conn_results:
            #    x_axis.append(tuple[0])
            #   y_axis.append(tuple[1])

            print('x_axis: ', x_axis)

        if self.autoscale != 'Yes':
            layout = go.Layout(title=title, yaxis=dict(range=[0, self.max_count]))
        else:
            layout = Layout(title=title)

        fig = go.Figure(data=[go.Scatter(x=x_axis, y=y_axis, mode=self.mode, marker=dict(color=self.bar_color.lower()))], layout=layout)

        if self.autoscale != 'Yes':
            fig.update_yaxes(dtick=self.increment_by)
        # graph = [Bar(x=x_axis,y=y_axis)]
        # layout = Layout(title='Length of Visits',xaxis=dict(title='Length (min)'),yaxis=dict(title='# of Visits'))
        # fig = Figure(data=graph,layout=layout)
        # plot_div = plot(fig,output_type='div',show_link=False,link_text="")

        # Dash instance for includng a table
        if self.include_table == 'Yes':
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
            table = go.Figure(data=[go.Table(header=dict(values=header), cells=dict(values=values))])

            app.layout = html.Div(children=[dcc.Graph(id='table', figure=table)
                , dcc.Graph(id='figure', figure=fig, style={'height': '80vh', 'width': '80vw'}),
                                            ], style={'height': '40vh', 'width': '70vw'})
        else:
            app.layout = html.Div(children=[
                dcc.Graph(id='figure', figure=fig, style={'height': '90vh'}),
            ], style={'height': '70vh', 'width': '70vw'})

        return app, title


def getReport(request):
    data = pageViews.preset_storage
    print('Data: ', data)
    reportGenerator = ReportGenerator(request, data)
    app, title = reportGenerator.generateReport()

    print('get report title: ', title)

    return render(request, 'visualizations/getReport.html', context={'graphTitle': title})


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
