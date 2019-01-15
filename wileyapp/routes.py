from flask import render_template, url_for, flash, redirect
from jinja2 import Template
import pprint
import json
import codecs

from wileyapp import app
from wileyapp.forms import *
from wileyapp.plotting import *

global courses_obj, course_name, course_obj, GPA

@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/", methods=['GET', 'POST'])
def home():
    form = TextForm()
    if form.validate_on_submit():
        global courses_obj, course_obj
        raw_text_input = form.text.data
        courses_obj = text2obj(raw_text_input)
        course_obj = courses_obj[0]
        return redirect(url_for('results'))
    return render_template('landing.html', form=form)


@app.route("/results", methods=['GET', 'POST'])
def results():
    global courses_obj
    return render_template('results.html', courses_obj=courses_obj)


# retrieve main ridgeplot
@app.route("/ridge_plot")
def ridge_plot():
    global courses_obj
    p = ridgeplot(courses_obj)
    return json.dumps(json_item(p))

# retrieve workload plot
@app.route("/workload_plot")
def workload_plot():
    global courses_obj
    print("OBELUEOUOEDLUREOGUDEORLDUEROGUDLOERDUROLEDULOEDGUEODURLOEUGDEUDLEDUREGODUGDLOEDUROE")
    p = workloadplot(courses_obj)
    #print(p)
    return json.dumps(json_item(p))

# retrieve individual plots
@app.route("/plot1/<course_name>")
def plot1(course_name):
    global courses_obj
    index = [x['course_name'] for x in courses_obj].index(course_name)

    course_obj = courses_obj[index]

    p = gradesplot(course_obj)
    return json.dumps(json_item(p))

# use this as a skeleton for the user to input weights in /result3
@app.route("/result2/", methods=['GET', 'POST'])
def result2():
    global courses_obj, course_obj, course_name, GPA
    # now ask how these categories are weighted
    index = 0
    while True:
        if courses_obj[index]['course_name'] == course_name:
            course_obj = courses_obj[index]
            break
        index += 1
    categories = get_categories(courses_obj[index]['assignments'])
    form = CategoryWeightsForm()
    for i in range(len(categories)):
        form.weights.append_entry()
        form.weights.entries[i].label = categories[i]
    if form.is_submitted():
        return redirect(url_for('result3'))
    return render_template('result2.html', course_name=course_name, form=form, categories=categories)