from pandas import read_csv
from models import cost

LISTINGS = read_csv('data/listings-filtered.csv', index_col=0)
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
    'guests_included': 26,
    'cost_score': 27
}

# To be able to do this here since cost scores always remain the same
cost.init_cost_scores(LISTINGS)

def get_all_listings():
    """
    Returns the Data frame containing the LISTINGS
    """
    return LISTINGS

def get_column_index(col_str):
    return COLUMNS[col_str]
