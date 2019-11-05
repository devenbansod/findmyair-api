import csv
import json

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

TRIP_COSTS = []
with open('./data/yellow_tripdata_copy.csv', 'r') as taxi_costs:
    listings = csv.reader(taxi_costs)
    for trip in listings:
        TRIP_COSTS.append(trip)

LAT_LONG = {}
with open('./data/zone_lat_lng_copy.json', 'r') as read_file:
    LAT_LONG = json.load(read_file)


def get_neighbourhood_id(lat, lng):
    lat_lng_map =  LAT_LONG["features"]
    neighbourhood_id = -1

    for obj in lat_lng_map:
        lng1 = float(obj["geometry"]["properties"]["bbox"][0])
        lat1 = float(obj["geometry"]["properties"]["bbox"][1])
        lng2 = float(obj["geometry"]["properties"]["bbox"][2])
        lat2 = float(obj["geometry"]["properties"]["bbox"][3])

        if check_if_point_falls_in_rect(lat1, lng1, lat2, lng2, lat, lng):
            return int(obj["geometry"]["properties"]["locationid"])

    return neighbourhood_id;

def avg_cost(pickup_lat, pickup_lng, drop_lat, drop_lng):
    pickup_lat = float(pickup_lat)
    pickup_lng = float(pickup_lng)
    drop_lat = float(drop_lat)
    drop_lng = float(drop_lng)

    pickup_id = get_neighbourhood_id(pickup_lat, pickup_lng)
    drop_id = get_neighbourhood_id(drop_lat, drop_lng)

    avg_cost = 0
    count = 0
    total_cost = 0

    if pickup_id != -1 and drop_id != -1:
        for trip in TRIP_COSTS:
            if (
                (int(trip[COLUMNS['PULocationID']]) == pickup_id and int(trip[COLUMNS['DOLocationID']]) == drop_id)
                or (int(trip[COLUMNS['DOLocationID']]) == pickup_id and int(trip[COLUMNS['PULocationID']]) == drop_id)
            ):
                total_cost = total_cost + float(trip[COLUMNS['total_amount']])
                count = count + 1

        if count != 0:
            avg_cost = total_cost / count

    return avg_cost

def check_if_point_falls_in_rect(lat1, lng1, lat2, lng2, lat, lng):
    if (lat >= min(lat1, lat2) and lat <= max(lat1, lat2)) and (lng >= min(lng1, lng2) and lng <= max(lng1, lng2)):
        return True
