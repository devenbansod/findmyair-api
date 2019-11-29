import json
from multiprocessing import Pool
import numpy as np 
from os import path
import pandas as pd
import tqdm
from sklearn.preprocessing import MinMaxScaler

from models import listings

COLUMNS = {
    'VendorID': 0,
    'tpep_pickup_datetime': 1,
    'tpep_dropoff_datetime': 2,
    'passenger_count': 3,
    'trip_distance': 4,
    'RatecodeID': 5,
    'store_and_fwd_flag': 6,
    'PULocationID': 7,
    'DOLocationID': 8,
    'payment_type': 9,
    'fare_amount': 10,
    'extra': 11,
    'mta_tax': 12,
    'tip_amount': 13,
    'tolls_amount': 14,
    'improvement_surcharge': 15,
    'total_amount': 16
}
     
# TRIP_COSTS = pd.read_csv('data/yellow_tripdata_jan_2018.csv', memory_map=True)
# Initializing to empty data frame to avoid errors ahead.
TRIP_COSTS = pd.DataFrame()

LAT_LONG = {}
with open('data/zone_lat_lng.json', 'r') as read_file:
    LAT_LONG = json.load(read_file)

POIS = []
with open('data/pois.json', 'r') as pois_file:
    POIS = json.load(pois_file)

LISTINGS = listings.get_all_listings()

def get_neighbourhood_id(lat, lng):
    lat_lng_map =  LAT_LONG["features"]
    neighbourhood_id = -1

    for obj in lat_lng_map:
        lng1 = float(obj["properties"]["bbox"][0])
        lat1 = float(obj["properties"]["bbox"][1])
        lng2 = float(obj["properties"]["bbox"][2])
        lat2 = float(obj["properties"]["bbox"][3])

        if check_if_point_falls_in_rect(lat1, lng1, lat2, lng2, lat, lng):
            return int(obj["properties"]["locationid"])

    return neighbourhood_id;

def avg_cost(pickup_lat, pickup_lng, drop_lat, drop_lng, brooklyn=False, brooklyn_pickup=False):
    pickup_lat = float(pickup_lat)
    pickup_lng = float(pickup_lng)
    drop_lat = float(drop_lat)
    drop_lng = float(drop_lng)

    pickup_id = get_neighbourhood_id(pickup_lat, pickup_lng)
    drop_id = get_neighbourhood_id(drop_lat, drop_lng)
    if pickup_id==103:
        pickup_id==12
    if drop_id==103:
        drop_id=12
    if brooklyn:
        if brooklyn_pickup:
            pickup_id=33
        else:
            drop_id=33

    avg_cost = 0
    count = 0
    total_cost = 0

    if pickup_id != -1 and drop_id != -1:
        cost_going = TRIP_COSTS[(TRIP_COSTS['PULocationID']==pickup_id) & (TRIP_COSTS['DOLocationID']==drop_id)]
        cost_returning = TRIP_COSTS[(TRIP_COSTS['PULocationID']==drop_id) & (TRIP_COSTS['DOLocationID']==pickup_id)]
        combined_cost = cost_going.append(cost_returning, ignore_index=True)
        if len(combined_cost) == 0:
            # One poi doesnt exist in map? Id=-1? Brooklyn bridge falls in no neighbourhood.
            return 0
        avg_cost = np.mean(combined_cost['total_amount'])

    return avg_cost

def check_if_point_falls_in_rect(lat1, lng1, lat2, lng2, lat, lng):
    if (lat >= min(lat1, lat2) and lat <= max(lat1, lat2)) and (lng >= min(lng1, lng2) and lng <= max(lng1, lng2)):
        return True

def get_travel_cost_airbnb(airbnb):
    # print("Airbnb:",airbnb)
    airbnb_travel_cost = np.zeros((len(POIS)))
    for poi in range(len(POIS)):
        if poi==4:
            airbnb_travel_cost[poi] = avg_cost(LISTINGS.loc[airbnb,'latitude'], LISTINGS.loc[airbnb,'longitude'], 
                                      POIS[poi]['details']['latitude'], POIS[poi]['details']['longitude'],brooklyn=True)
        else:
            airbnb_travel_cost[poi] = avg_cost(LISTINGS.loc[airbnb,'latitude'], LISTINGS.loc[airbnb,'longitude'], 
                                      POIS[poi]['details']['latitude'], POIS[poi]['details']['longitude'],brooklyn=False)
    
    return airbnb, airbnb_travel_cost


def get_travel_cost_matrix():
    # Generate the M*N travel cost matrix using the yellow taxi data.
    # M is the number of Airbnb's and N is the number of points of interest. 
    # Each entry (i,j) represents the average cost of going from i_th Airbnb to the j_th point of interest.
    if not path.exists("data/travel_cost_matrix.npy"):
        scaler = MinMaxScaler()
        # For each Airbnb abd poi pair, get the average cost
        pool = Pool(processes=7)
        airbnb_taxi_costs = pool.map(get_travel_cost_airbnb, range(LISTINGS.shape[0]))
        pool.close()
        pool.join()
        # Sorting the airbnb index wise
        airbnb_taxi_costs = sorted(airbnb_taxi_costs, key= lambda x: x[0])
        airbnb_taxi_costs = np.vstack([ab[1] for ab in airbnb_taxi_costs])
        airbnb_taxi_costs = scaler.fit_transform(airbnb_taxi_costs)
        np.save("data/travel_cost_matrix.npy", airbnb_taxi_costs)

def update_travel_cost():
    travel_cost_matrix = np.load("../data/travel_cost_matrix.npy")
    for airbnb in tqdm.tqdm(range(LISTINGS.shape[0])[:100]):
        airbnb_id = get_neighbourhood_id(float(LISTINGS.loc[airbnb, 'latitude']), float(LISTINGS.loc[airbnb, 'longitude']))
        for poi in range(len(POIS)):
            poi_id = get_neighbourhood_id(float(POIS[poi]['details']['latitude']), float(POIS[poi]['details']['longitude']))
            if airbnb_id!=-1 and airbnb_id==poi_id:
                # Same id's so update cost to be non zero it already isnt
                if travel_cost_matrix[airbnb, poi] == 0.0:
                    travel_cost_matrix[airbnb,poi] = 0.01

def get_poi_travel_cost():
    if not path.exists("data/poi_travel_cost_matrix.npy"):
        scaler = MinMaxScaler()
        # For each Airbnb abd poi pair, get the average cost
        poi_taxi_costs = np.zeros((len(POIS), len(POIS)))
        for poi1 in range(len(POIS)):
            for poi2 in range(len(POIS)):
                if poi1==poi2 or poi1>poi2:
                    continue
                else:
                    if poi1==4:
                        poi_taxi_costs[poi1,poi2] = avg_cost(POIS[poi1]['details']['latitude'], POIS[poi1]['details']['longitude'], 
                                      POIS[poi2]['details']['latitude'], POIS[poi2]['details']['longitude'], brooklyn=True, brooklyn_pickup=True)
                    elif poi2==4:
                        poi_taxi_costs[poi1,poi2] = avg_cost(POIS[poi1]['details']['latitude'], POIS[poi1]['details']['longitude'], 
                                      POIS[poi2]['details']['latitude'], POIS[poi2]['details']['longitude'],brooklyn=True, brooklyn_pickup=False)
                    else:
                        poi_taxi_costs[poi1,poi2] = avg_cost(POIS[poi1]['details']['latitude'], POIS[poi1]['details']['longitude'], 
                                      POIS[poi2]['details']['latitude'], POIS[poi2]['details']['longitude'],brooklyn=False)

                    # poi_taxi_costs[poi2,poi1] = poi_taxi_costs[poi1,poi2]    
        # Sorting the airbnb index wise
        np.save("data/poi_travel_cost_matrix.npy", poi_taxi_costs)


# if __name__ == '__main__':
#     update_travel_cost()
#     get_travel_cost_matrix()