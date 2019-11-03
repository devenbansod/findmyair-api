import csv

COLUMNS = {
    'id': 0,
    'listing_url': 1,
    'name': 2,
    'picture_url': 3,
    'neighbourhood': 4,
    'neighbourhood_cleansed': 5,
    'neighbourhood_group_cleansed': 6,
    'city': 7,
    'state': 8,
    'zipcode': 9,
    'market': 10,
    'smart_location': 11,
    'country_code': 12,
    'country': 13,
    'latitude': 14,
    'longitude': 15,
    'is_location_exact': 16,
    'property_type': 17,
    'room_type': 18,
    'accommodates': 19,
    'bathrooms': 20,
    'bedrooms': 21,
    'beds': 22,
    'bed_type': 23,
    'square_feet': 24,
    'price': 25,
    'guests_included': 26
}

LISTINGS = []
with open('./data/listings-filtered.csv', 'r') as listings_file:
    listings = csv.reader(listings_file)
    for airbnb in listings:
        LISTINGS.append(airbnb)

def get_airbnb(airbnb_id):        
    for airbnb in LISTINGS:
        if airbnb[COLUMNS['id']] == str(airbnb_id):
            ret = {}
            for key in COLUMNS.keys():
                ret[key] = airbnb[COLUMNS[key]]

            return ret

    return {}

def get_cost_for_airbnb(airbnb_id):
    airbnb = get_airbnb(airbnb_id)
    if 'price' in airbnb.keys():
        return airbnb['price']

    return -1

def get_cost_metric(airbnb_id):
    pass
