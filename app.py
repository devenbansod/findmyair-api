from flask import Flask
from flask import request
from flask import json
from flask import jsonify

import os
import csv
from models import listings
import numpy as np
import json

from sklearn.preprocessing import MinMaxScaler

from models import taxicost

app = Flask(__name__)
API_KEY = os.environ.get('API_KEY', None)
POIS = None
CRIME_SCORES = None
TAXI_COST = None

with open('./data/pois.json', 'r') as pois_file:
    POIS = {
        "listings": json.loads(pois_file.read())
    }

CRIME_SCORES = np.load("data/crime_scores.npy")
TAXI_COST = np.load("data/travel_cost_matrix.npy")
with open("data/review_sentiments.json", 'r') as fp:
    REVIEW_SENTIMENTS = json.load(fp)

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
    listings_with_scores = filter_suggested_airbnbs(listings_with_scores)
    listings_with_scores.sort(key=lambda x: x['suitability_score'], reverse=True)

    page = int(request.args.get('page')) if request.args.get('page') != None else 1
    count = int(request.args.get('count')) if request.args.get('count') != None else 10

    # Sorting the listings on this page using their sentiment scores
    listings_on_page = listings_with_scores[page*count: page*count + count]
    ids_on_page = [x['id'] for x in listings_on_page]
    review_scores_on_page = np.array([REVIEW_SENTIMENTS[str(ids)]['average_sentiment'] for ids in ids_on_page])
    sorted_args = np.argsort(review_scores_on_page)
    review_sorted_listings = list(np.array(listings_on_page)[sorted_args])
    print(review_scores_on_page)
    print(ids_on_page)
    return {
        'suggestions': review_sorted_listings,
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
def filter_suggested_airbnbs(suggestions):
    suggestions = [ab for ab in suggestions if (ab['travel_score']<1.0)]
    return suggestions

def get_listings_with_scores(cost_pref, travel_cost_pref, safety_pref, iternaries):
    LISTINGS = listings.get_all_listings()
    ret = []
    # Calculating the taxi cost first so we can normalize it. Then add to the final dictionary.
    all_taxi_cost = np.zeros(LISTINGS.shape[0])
    for index in range(LISTINGS.shape[0]):
        temp_taxi_cost = 0.0
        for day in iternaries:
            temp_taxi_cost += (TAXI_COST[index, day[0]] + TAXI_COST[index, day[-1]])
        temp_taxi_cost /= len(iternaries)
        all_taxi_cost[index] = temp_taxi_cost

    scaler = MinMaxScaler()
    all_taxi_cost = np.expand_dims(all_taxi_cost,1)
    all_taxi_cost = scaler.fit_transform(all_taxi_cost)

    for index, airbnb in enumerate(LISTINGS.itertuples()):
        airbnb_id = airbnb[listings.get_column_index('id')]
        cost_score = 1 - airbnb[listings.get_column_index('cost_score')] 
        crime_score = 1 - CRIME_SCORES[index,0]
        taxi_score = 1 - all_taxi_cost[index,0]
        
        suitability_score = ((cost_score * cost_pref) + (crime_score * safety_pref) + 
                             (taxi_score* travel_cost_pref)) * 0.01

        # Adding an entry in review sentiments if airbnb id does not exist
        if REVIEW_SENTIMENTS.get(airbnb_id, -1) == -1:
            REVIEW_SENTIMENTS[str(airbnb_id)] = {'average_sentiment':0, 'total_pos':0, 'total_neg':0}

        ret.append({
            'id': airbnb_id,
            'url': airbnb[listings.get_column_index('listing_url')],
            'latitude': airbnb[listings.get_column_index('latitude')],
            'longitude': airbnb[listings.get_column_index('longitude')],
            'cost_score': cost_score,
            'safety_score': crime_score,
            'travel_score': taxi_score,
            'suitability_score': suitability_score,
            'name': airbnb[listings.get_column_index('name')]
        })

    return ret