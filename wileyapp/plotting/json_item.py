from __future__ import print_function
import json

from bokeh.embed import json_item
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.sampledata.iris import flowers

from flask import Flask
from jinja2 import Template

app = Flask(__name__)

page = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
  {{ resources }}
</head>

<body>
  <p>First Plot right here!:</p>
  <div id="myplot"></div>
  <p>After first plot, and then second plot:</p>
  <div id="myplot2"></div>
  <p>After second plot (should be)</p>
  <script>
  fetch('/plotone')
    .then(function(response) { return response.json(); })
    .then(function(item) { Bokeh.embed.embed_item(item); })
  </script>
  <script>
  fetch('/plottwo')
    .then(function(response) { return response.json(); })
    .then(function(item) { Bokeh.embed.embed_item(item, "myplot2"); })
  </script>
</body>
""")

colormap = {'setosa': 'red', 'versicolor': 'green', 'virginica': 'blue'}
colors = [colormap[x] for x in flowers['species']]

def make_plot(x, y):
    p = figure(title = "Iris Morphology", sizing_mode="fixed", plot_width=400, plot_height=400)
    p.xaxis.axis_label = x
    p.yaxis.axis_label = y
    p.circle(flowers[x], flowers[y], color=colors, fill_alpha=0.2, size=10)
    return p

@app.route('/')
def root():
    return page.render(resources=CDN.render())

@app.route('/plotone')
def plotone():
    p = make_plot('petal_width', 'petal_length')
    return json.dumps(json_item(p, "myplot"))

@app.route('/plottwo')
def plottwo():
    p = make_plot('sepal_width', 'sepal_length')
    return json.dumps(json_item(p))

if __name__ == '__main__':
    app.run()
