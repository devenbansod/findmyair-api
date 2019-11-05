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
    def test_debug_cost(self):
        with app.test_client() as c:

            # test debug cost
            rv = c.get('/debug/cost?id=21456')
            json_data = rv.get_json()

            assert json_data != {}
            assert json_data['id'] == '21456'

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
            expected_response = {'a' : 1}
            rv = c.post('/suggested-airbnbs', json=expected_response)
            assert rv.status_code == 200
            assert rv.get_json() == expected_response

if __name__ == "__main__":
    unittest.main()
