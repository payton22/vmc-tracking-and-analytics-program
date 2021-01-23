from django.shortcuts import render
from plotly.offline import plot
from plotly.graph_objs import Bar
from plotly.graph_objs import Figure
from plotly.graph_objs import Layout
import random
from pages import views as pageViews

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
        self.barGraph = State(data, self)
        self.histogram = State(data, self)
        self.lineGraph = State(data, self)
        self.pieChart = State(data, self)
        self.scatterPlot = State(data, self)
        self.individualStatistic = State(data, self)

        self.state = State(data, self)
        self.state = self.barGraph

    def setState(self, state):
        self.state = state

    def generateReport(self):
        self.state.generateReport()


class State:


    def generateReport(self):
        pass

    def checkDates(self):
        pass

    def checkIfPreset(self):
        pass

    def checkGraphType(self, data):
        pass

class BarGraph(State):
    def findState(self, data, rGenerator):
        self.reportGenerator = rGenerator
        inner_dict = data['form_data']
        graph_type = inner_dict[0]

        if graph_type['graphType'] == 'Bar Graph':
            self.reportGenerator.setState(self)
            print('It\'s a Bar Graph')

    def generateReport(self):



# Select count from visits where date >= from_date and date <= to_date group by location




def getReport(request):
    data = pageViews.preset_storage
    reportGenerator = ReportGenerator(data)
    return render(request, 'visualizations/getReport.html')


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

    import sqlite3;

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
