from pandas import read_csv
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler

LISTINGS = read_csv("data/listings-filtered.csv", index_col=0)
# Filter rows with price as 0.
LISTINGS = LISTINGS[LISTINGS.price>0]
LISTINGS = LISTINGS.reset_index(drop=True)

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

def init_cost_scores():
    global LISTINGS
    scaler = MinMaxScaler()

    LISTINGS['cost_score'] = LISTINGS.apply(lambda row: row.price, axis = 1) 
    df =  LISTINGS['cost_score'].copy()

    # with normalized price
    # LISTINGS[['cost_score']] = scaler.fit_transform(LISTINGS[['cost_score']])
    perc_75 = np.percentile(df, 75)
    min_score = min(df)
    mask = df > perc_75
    df[mask] = 1
    df[~mask] = (df[~mask] - min_score)/perc_75
    LISTINGS['cost_score'] = df

    # LISTINGS.loc[LISTINGS.cost_score <= perc_75]['cost_score'] = ((LISTINGS.loc[LISTINGS.cost_score < perc_75]['cost_score'] - min_score)/perc_75)
    # print(LISTINGS.cost_score.describe())

def get_all_listings():
    """
    Returns the Data frame containing the LISTINGS
    """
    return LISTINGS

def get_column_index(col_str):
    return COLUMNS[col_str]

# To be able to do this here since cost scores always remain the same
init_cost_scores()