"""
Routes and views for the flask application.
"""
import json
import urllib.request
import os

from datetime import datetime
from flask import render_template, request, redirect
from FlaskAppAML import app

from FlaskAppAML.forms import SubmissionForm

# Deployment environment variables defined on Azure (pull in with os.environ)
API_KEY = os.environ.get('API_KEY', "bqbOx/ih7sqf0YpFbTEBf9wyPA7WPcGGOomvMrTvwq4CC0KxgVPkU2grDnzYN/zqpx5xFUNWl1LOEK+C8L5zMw==")
URL = os.environ.get('URL', "https://ussouthcentral.services.azureml.net/workspaces/db57e3c91aeb4c4c8c5b831eb3aa0bd5/services/375cb1234d0d4dc0b29774e6212acee5/execute?api-version=2.0&details=true")

# Construct the HTTP request header
HEADERS = {'Content-Type':'application/json', 'Authorization':('Bearer '+ API_KEY)}

# Our main app page/route
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    """Renders the home page which is the CNS of the web app currently, nothing pretty."""

    form = SubmissionForm(request.form)

    # Form has been submitted
    if request.method == 'POST' and form.validate():

        # Plug in the data into a dictionary object 
        #  - data from the input form
        #  - text data must be converted to lowercase
        data =  {
              "Inputs": {
                "input1": {
                  "ColumnNames": [
                    "Title",
                    "Category",
                    "Text"
                  ],
                  "Values": [ [
                      form.title.data,
                      form.category.data,
                      form.text.data.lower()
                    ]
                  ]
                }
              },
              "GlobalParameters": {}
            }

        # Serialize the input data into json string
        body = str.encode(json.dumps(data))

        # Formulate the request
        req = urllib.request.Request(URL, body, HEADERS)

        # Send this request to the AML service and render the results on page
        try:
            # response = requests.post(URL, headers=HEADERS, data=body)
            response = urllib.request.urlopen(req)
            respdata = response.read()
            result = json.loads(str(respdata, 'utf-8'))
            result = do_something_pretty(result)
            # result = json.dumps(result, indent=4, sort_keys=True)
            return render_template(
                'result.html',
                title="From your friendly AML experiment's Web Service:",
                result=result)

        # An HTTP error
        except Exception as err:
            result = json.loads(str(err.code))
            return render_template(
                'result.html',
                title='There was an error',
                result=result)

    # Just serve up the input form
    return render_template(
        'form.html',
        form=form,
        title='Run App',
        year=datetime.now().year,
        message='Input form to gain insights into a company using Azure Machine Learning')


@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

def do_something_pretty(jsondata):
    """We want to process the AML json result to be more human readable and understandable"""
    import itertools # for flattening a list of tuples below

    # We only want the first array from the array of arrays under "Value" 
    # - it's cluster assignment and distances from all centroid centers from k-means model
    value = jsondata["Results"]["output1"]["value"]["Values"][0]
    valuelen = len(value)

    # Convert values (a list) to a list of tuples [(cluster#,distance),...]
    valuetuple = list(zip(range(valuelen-1), value[1:(valuelen)]))
    # Convert the list of tuples to one long list (flatten it)
    valuelist = list(itertools.chain(*valuetuple))

    # Convert to a tuple for the list
    data = tuple(list(value[0]) + valuelist)

    # Build a placeholder for the cluster#,distance values
    repstr = '<tr><td>%d</td><td>%s</td></tr>' * (valuelen-1)

    # Build the entire html table for the results data representation
    tablestr = 'Cluster assignment: %s<br><br><table border="1"><tr><th>Cluster</th><th>Distance From Center</th></tr>'+ repstr + "</table>"
    return tablestr % data
