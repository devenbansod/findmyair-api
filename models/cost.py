from models import listings
from sklearn.preprocessing import StandardScaler, MinMaxScaler


def init_cost_scores(listings_list):
    scaler = MinMaxScaler()

    listings_list['cost_score'] = listings_list.apply(lambda row: row.price, axis = 1) 

    # with normalized price
    listings_list[['cost_score']] = scaler.fit_transform(listings_list[['cost_score']])
