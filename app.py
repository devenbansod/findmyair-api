from flask import Flask
from flask import request
from flask import json

import os
import csv

from models import cost

app = Flask(__name__)
API_KEY = os.environ.get('API_KEY', None)
POIS = None

with open('./data/pois.json', 'r') as pois_file:
    POIS = {
        "listings": json.loads(pois_file.read())
    }

# MAIN APIS
@app.route('/pois', methods = ['GET'])
def get_pois():
    return POIS

@app.route('/suggested-airbnbs', methods = ['POST'])
def get_suggested_airbnbs():
    return request.json



# TEST DEBUG APIS - ideally should be prepended with /debug path
@app.route('/debug/cost')
def get_cost_metric():
    return cost.get_airbnb(request.args.get('id'))
