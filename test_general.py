from flask import Flask, request, jsonify, url_for
from app import app
import json
import unittest


POIS = {}
with open('./data/pois.json', 'r') as pois_file:
    POIS = {
        "listings": json.loads(pois_file.read())
    }

class TestAPIs(unittest.TestCase):
    def test_debug_travel_cost(self):
        with app.test_client() as c:
            # test debug travel cost
            rv = c.post('/debug/travel-cost', json={
                "pickup_lat": "40.69509499999986",
                "pickup_lng": "-74.18448899999997",
                "drop_lat": "40.61480534006002",
                "drop_lng": "-73.83009815098022"
            })
            assert rv.status_code == 200

    def test_pois(self):
        with app.test_client() as c:
            # test POI
            rv = c.get('/pois')
            assert rv.status_code == 200
            assert rv.get_json() == POIS

    def test_suggested_airbnbs(self):
        with app.test_client() as c:
            # test suggested airbnbs
            request = {
                "preferences": {
                    "cost": 0.34,
                    "travel": 0.54,
                    "safety": 0.12
                },
                "iternaries": [
                    [8, 5, 1],
                    [9, 2, 7]
                ]
            }
            rv = c.post('/suggested-airbnbs', json=request)
            assert rv.status_code == 200

if __name__ == "__main__":
    unittest.main()
