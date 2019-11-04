from flask import Flask
from flask import request
from flask import json

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
@app.route('/debug/cost')
def get_cost_metric():
    return cost.get_airbnb(request.args.get('id'))

@app.route('/travel-cost', methods = ['POST'])
def get_travel_cost():
	data = request.data
	data = jsonify(data)
	return taxicost.avg_cost(data.pickupLat,data.pickupLng,data.dropLat,data.dropLng)

#testing the function avg_cost
print(taxicost.avg_cost("40.69509499999986","-74.18448899999997","40.61480534006002","-73.83009815098022"))
