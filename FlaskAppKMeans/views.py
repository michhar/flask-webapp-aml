"""
Routes and views for the flask application.
"""
import json
import urllib

from datetime import datetime
from flask import render_template, request, redirect
from FlaskAppKMeans import app
from FlaskAppKMeans.forms import SubmissionForm

API_KEY = 'bqbOx/ih7sqf0YpFbTEBf9wyPA7WPcGGOomvMrTvwq4CC0KxgVPkU2grDnzYN/zqpx5xFUNWl1LOEK+C8L5zMw=='
URL = 'https://ussouthcentral.services.azureml.net/workspaces/db57e3c91aeb4c4c8c5b831eb3aa0bd5/services/375cb1234d0d4dc0b29774e6212acee5/execute?api-version=2.0&details=true'
HEADERS = {'Content-Type':'application/json', 'Authorization':('Bearer '+ API_KEY)}

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    """Renders the home page which is the CNS of the web app currently."""

    form = SubmissionForm(request.form)

    # Form has been submitted
    if request.method == 'POST' and form.validate():

        # Plug in the data into a dictionary object
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

        # Serialize the data into json
        body = str.encode(json.dumps(data))

        # Formulate the request
        req = urllib.request.Request(URL, body, HEADERS)

        # Send this request to the AML service
        try:
            response = urllib.request.urlopen(req)
            result = response.read()
            print(result)
            return render_template(
                'result.html',
                title='Successful request!',
                result=result)

        # An HTTP error
        except urllib.error.HTTPError as err:
            result = json.loads(str(err.code))
            return render_template(
                'result.html',
                title='There was an error',
                result=result)

    # Just serve up the input form
    return render_template(
        'form.html',
        form=form)


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

