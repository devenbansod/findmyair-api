from flask import Flask
from flask import request
from flask import json
from flask import jsonify

import os
import csv
from models import listings

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
    data = request.json
    preferences = data['preferences']

    cost_pref = preferences['cost']
    travel_cost_pref = preferences['travel']
    safety_pref = preferences['safety']

    iternaries = data['iternaries']

    # [ {id, url, cost_score, travel_score, safety_score, lat, lng, suitability_score} ]
    listings_with_scores = get_listings_with_scores(cost_pref, travel_cost_pref, safety_pref, iternaries)
    listings_with_scores.sort(key=lambda x: x['suitability_score'], reverse=True)

    page = int(request.args.get('page')) if request.args.get('page') != None else 1
    count = int(request.args.get('count')) if request.args.get('count') != None else 10

    return {
        'suggestions': listings_with_scores[page*count: page*count + count],
        'count': count,
        'page': page,
        'total': len(listings_with_scores)
    }

# TEST DEBUG APIS - ideally should be prepended with /debug path
@app.route('/debug/travel-cost', methods = ['POST'])
def get_travel_cost():
    data = request.json

    return str(taxicost.avg_cost(data['pickup_lat'], data['pickup_lng'], data['drop_lat'], data['drop_lng']))

# print(taxicost.avg_cost("40.69509499999986","-74.18448899999997","40.61480534006002","-73.83009815098022"))

def get_listings_with_scores(cost_pref, travel_cost_pref, safety_pref, iternaries):
    LISTINGS = listings.get_all_listings()
    ret = []

    for airbnb in LISTINGS.itertuples():
        cost_score = airbnb[listings.get_column_index('cost_score')]
        suitability_score = cost_score * cost_pref

        ret.append({
            'id': airbnb[listings.get_column_index('id')],
            'url': airbnb[listings.get_column_index('listing_url')],
            'latitude': airbnb[listings.get_column_index('latitude')],
            'latitude': airbnb[listings.get_column_index('latitude')],
            'cost_score': airbnb[listings.get_column_index('cost_score')],
            'suitability_score': suitability_score
        })

    return ret