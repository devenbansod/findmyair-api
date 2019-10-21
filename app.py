from flask import Flask
from flask import request

import geopy.distance

app = Flask(__name__)

@app.route('/')
def hello():
    lat1 = float(request.args.get('lat1'))
    lat2 = float(request.args.get('lat2'))
    long1 = float(request.args.get('long1'))
    long2 = float(request.args.get('long2'))

    if not lat1:
        return 'lat1 not provided'

    if not lat2:
        return 'lat2 not provided'

    if not long1:
        return 'long1 not provided'

    if not long2:
        return 'long2 not provided'

    coords_1 = (lat1, long1)
    coords_2 = (lat2, long2)

    return 'Distance is: ' + str(geopy.distance.vincenty(coords_1, coords_2).km)