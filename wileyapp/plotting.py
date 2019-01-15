from bokeh.embed import json_item
from bokeh.plotting import figure, ColumnDataSource
from bokeh.resources import CDN
from bokeh.plotting import *
from bokeh.models.tools import PanTool, CrosshairTool, HoverTool, SaveTool, BoxZoomTool, WheelZoomTool, ResetTool
from bokeh.models import HoverTool
from bokeh.palettes import Spectral
from bokeh.models.tickers import FixedTicker
from bokeh.models.formatters import PrintfTickFormatter

from wileyapp.mybackpack_parsing import *

from collections import OrderedDict
import numpy as np
import pandas as pd
from scipy.stats.kde import gaussian_kde
import sys
import colorcet as cc
import itertools
import time

TWO_WEEKS=1209600 # microseconds in two weeks

DIVISION=10**9

# what do we want to plot?
# 1. grades across time

#workload plot (number of assignments in a given time period, plot as ridgeplot)
# also maybe mention that you're weighting "tests" 4x more and "exams" 10x more, assignments 1x
# just for time spent

# maybe format it like a matrix-ish heat map like this
# (https://www.kaggle.com/neerjad/time-series-visualization-using-bokeh)
# one-week time spans
# have it count the number of assignments due that week
def workloadplot(courses_obj, is_ridge=True):
    # we just need to first get a list of lists of dicts
    # each sublist is a separate course
    # within each sublist you're gonna have a bunch of datetimes
    # for each datetime, you want to repeat it depending on the category
    datetimes = [[[xi[5]]*repeat(xi[1].lower()) for xi in x['assignments']] for x in courses_obj]
    datetimes = [list(itertools.chain.from_iterable(x)) for x in datetimes]
    datetimes = pd.DataFrame(datetimes, index=[x['course_name'] for x in courses_obj]).transpose()
    datetimes = datetimes.apply(pd.to_datetime) # convert to datetime
    datetimes = pd.DataFrame([datetimes[x].dt.week for x in datetimes])

    counts = pd.DataFrame([datetimes[x].value_counts() for x in datetimes]).transpose()
    #counts = 
    # use something like a[0].combine(pd.Series([0 for x in range(50)]), lambda x1, x2: x1 if type(x1)==type(pd.to_datetime('8/8/2018')) else pd.to_datetime('1/1/2018' ))

    assert(datetimes.shape[1] == len(courses_obj))

    # for each course, need a list where each element is the number of assignments
    # due that week (by index)
    first_date = time.mktime(datetimes.apply(min).min().timetuple())
    last_date = time.mktime(datetimes.apply(max).max().timetuple())

    x = np.arange(first_date, last_date+DIVISION, TWO_WEEKS)
    x_ = np.linspace(0,101,2)

    source = ColumnDataSource(data=dict(x_=x_))

    cats = list(datetimes.keys())



    p.outline_line_color = None
    p.background_fill_color = "#efefef"

    p.tools = [PanTool(), CrosshairTool(), HoverTool(), SaveTool(), BoxZoomTool(), WheelZoomTool(), ResetTool()]
    p.xaxis.axis_label = "Your Workload Over Time"

    p.yaxis.axis_label = "Your Courses"

    p.ygrid.grid_line_color = None
    p.xgrid.grid_line_color = "Grey"

    #ticks = ['Beginning', 'End']
    #p.xaxis.ticker = FixedTicker(ticks=ticks)

    p.xgrid.ticker = p.xaxis[0].ticker

    p.axis.minor_tick_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.axis_line_color = None

    p.y_range.range_padding = 0.8
    #p.y_range.group_padding = 3

    return p


# like this https://bokeh.pydata.org/en/latest/docs/gallery/ridgeplot.html
def ridgeplot(courses_obj):
    # first format 'courses_obj' into 'probly' DataFrame format
    # courses_obj: [{'course_name': 'Calculus...', ...}, ...]
    grades = [[100*y[2]/y[3] for y in x['assignments']] for x in courses_obj]
    # turn this list of lists into a complete NumPy array
    length = len(sorted(grades, key=len, reverse=True)[0])
    grades = np.array([xi+[None]*(length-len(xi)) for xi in grades], dtype='float')
    columns = [x['course_name'] for x in courses_obj]
    grades = grades.transpose()
    probly = pd.DataFrame(grades, columns=columns)


    cats = list(reversed(probly.keys()))


    palette = [cc.rainbow[i*15] for i in range(17)]

    x = np.linspace(-20,110, 500)

    source = ColumnDataSource(data=dict(x=x))

    p = figure(y_range=cats, plot_width=900, plot_height = 300, x_range=(-5, 120))#, toolbar_location=None)

    for i, cat in enumerate(reversed(cats)):
        adjusted = probly[cat].replace([np.inf, -np.inf], np.nan).dropna(how="all")
        if adjusted.size == 1 or pd.unique(adjusted).size == 1: # this means we can't compute
            continue
        pdf = gaussian_kde(adjusted)
        #p = figure(plot_width=400, plot_height=400)
        #p.line(x, pdf(x))
        y = ridge(cat, pdf(x), scale=2)
        #p.line(x, y, color='black')
        #show(p)
        source.add(y, cat)
        p.patch('x', cat, color=palette[i], alpha=0.6, line_color="black", source=source)

    p.outline_line_color = None
    p.background_fill_color = "#efefef"

    p.tools = [PanTool(), CrosshairTool(), HoverTool(), SaveTool(), BoxZoomTool(), WheelZoomTool(), ResetTool()]

    ticks = list(np.array([np.array([0,3,7])+i*10 for i in range(10)]).flatten()) + [100]
    p.xaxis.ticker = FixedTicker(ticks=ticks)
    p.xaxis.formatter = PrintfTickFormatter(format="%d")
    p.xaxis.axis_label = "Your Grade Distribution"

    p.yaxis.axis_label = "Your Courses"

    p.ygrid.grid_line_color = None
    p.xgrid.grid_line_color = "Grey"
    p.xgrid.ticker = p.xaxis[0].ticker

    p.axis.minor_tick_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.axis_line_color = None

    p.y_range.range_padding = 0.12

    return p


# should also do a circular time graph plot

def gradesplot(course_obj):
    assignment_array = course_obj['assignments']
    assignment_array.reverse()
    all_categories = get_categories(assignment_array)
    # get a list of lists
    # so each list within has all of the assignments belonging to that category/group
    data = []
    for category in all_categories:
        category_data = []
        for assignment in assignment_array:
            if assignment[1] == category:
                category_data.append(assignment)
        data.append(category_data)
    p = figure(x_axis_type="datetime", plot_width=1000, plot_height=300, y_range=(50,120))
    p.title.text = "Grades over time"

    colors = Spectral[len(all_categories)] if len(all_categories) >= 3 else Spectral[3][:len(all_categories)]
    
    assert(len(data) == len(all_categories) == len(colors))

    for datum, category, color in zip(data, all_categories, colors):
        df = pd.DataFrame(datum)
        df = df.rename({0:'name',1:'grouping', 2:'score', 3:'possible',4:'assigned',5:'due'}, axis='columns')

        df['due'] = pd.to_datetime(df['due'])
        source = ColumnDataSource(data=dict(
                x=df['due'],
                y=100*df['score']/df['possible'],
                category=df['grouping'],
                name=df['name']
            ))
        p.line('x', 'y', line_width=2, color=color, source=source, legend=category, tags=[category])
        p.circle('x', 'y', color=color, legend=category, source=source, tags=[category])

    p.ygrid.grid_line_alpha = 0.75
    p.ygrid.grid_line_color = "Black"
    p.legend.location = "bottom_left"
    p.legend.click_policy="hide"
    p.legend.label_text_font_size = '8pt'
    p.legend.spacing = -6

    p.toolbar.logo = None
    p.tools = [PanTool(), CrosshairTool(), HoverTool(), SaveTool(), BoxZoomTool(), WheelZoomTool(), ResetTool()]

    hover = p.select(dict(type=HoverTool))
    hover.tooltips = """
        <style>
            .bk-tooltip>div:not(:first-child) {display:none;}
        </style>
        <span style="font-size: 12px;">@name</span>
        <span style="font-size: 10px;"> (@category) <br>
        Grade: @y%</span>
    """

    return p


if __name__ == '__main__':
    pass










