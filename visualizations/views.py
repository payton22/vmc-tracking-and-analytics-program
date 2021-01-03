from django.shortcuts import render
from plotly.offline import plot
from plotly.graph_objs import Bar
from plotly.graph_objs import Figure
from plotly.graph_objs import Layout
import random

def plotly(request):
    demographics = ['WHITE','BLACK','HISPA','ASIAN','UNKWN']
    average_visits = [random.uniform(1.5,6) for x in demographics]
    graph = [Bar(x=demographics,y=average_visits)]
    layout = Layout(title='Average # of Visits by Ethnicity',xaxis=dict(title='Ethnicity'),yaxis=dict(title='Average # of Visits'))
    fig = Figure(data=graph,layout=layout)
    plot_div = plot(fig,output_type='div',show_link=False,link_text="")
    return render(request, "visualizations/plotly.html", context={'plot_div':plot_div})

# Create your views here.
