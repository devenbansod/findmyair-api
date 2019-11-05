from flask import Flask
from flask import request
from flask import json
from flask import jsonify

import os
import csv

from models import cost
from models import taxicost

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
@app.route('/debug/cost', methods = ['GET'])
def get_cost_metric():
    return cost.get_airbnb(request.args.get('id'))

@app.route('/debug/travel-cost', methods = ['POST'])
def get_travel_cost():
    data = request.json

    return str(taxicost.avg_cost(data['pickup_lat'], data['pickup_lng'], data['drop_lat'], data['drop_lng']))

# print(taxicost.avg_cost("40.69509499999986","-74.18448899999997","40.61480534006002","-73.83009815098022"))

