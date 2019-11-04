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

COSTS = []
with open('./data/yellow_tripdata_copy.csv', 'r') as taxi_costs:
    listings = csv.reader(taxi_costs)
    for cost in listings:
        COSTS.append(cost)

LAT_LNG = {}
with open('./data/zone_lat_lng_copy.json', 'r') as read_file:
    LAT_LNG = json.load(read_file)


def get_id(pickupLat,pickupLng,dropLat,dropLng): 
    pickupLat = float(pickupLat)
    pickupLng = float(pickupLng)
    dropLat = float(dropLat)
    dropLng = float(dropLng)
    lat_lng =  LAT_LNG["features"]
    pickupId = -1
    dropId = -1
    for obj in lat_lng:
        lng1 = float(obj["geometry"]["properties"]["bbox"][0])
        lat1 = float(obj["geometry"]["properties"]["bbox"][1])
        lng2 = float(obj["geometry"]["properties"]["bbox"][2])
        lat2 = float(obj["geometry"]["properties"]["bbox"][3])
        if(pickupLat >= min(lat1,lat2) and pickupLat <= max(lat1,lat2)):
            if(pickupLng >= min(lng1,lng2) and pickupLng<= max(lng1,lng2)):
                pickupId = int(obj["geometry"]["properties"]["locationid"])
                break;

    for obj in lat_lng:
        lng1 = float(obj["geometry"]["properties"]["bbox"][0])
        lat1 = float(obj["geometry"]["properties"]["bbox"][1])
        lng2 = float(obj["geometry"]["properties"]["bbox"][2])
        lat2 = float(obj["geometry"]["properties"]["bbox"][3])
        if(dropLat >= min(lat1,lat2) and dropLat <= max(lat1,lat2)):
            if(dropLng >= min(lng1,lng2) and dropLng<= max(lng1,lng2)):
                dropId = int(obj["geometry"]["properties"]["locationid"])
                break;

    return {"pickupLocationID" : pickupId, "dropLocationId" : dropId}

def avg_cost(pickupLat,pickupLng,dropLat,dropLng):
    obj = get_id(pickupLat,pickupLng,dropLat,dropLng)
    avg_cost = 0
    count = 0
    total_cost = 0
    if(obj["pickupLocationID"] != -1 and obj["dropLocationId"] != -1):
        for cost in COSTS:
            if int(cost[COLUMNS['PULocationID']]) == obj["pickupLocationID"] and int(cost[COLUMNS['DOLocationID']]) == obj["dropLocationId"]:
                total_cost = total_cost + float(cost[COLUMNS['total_amount']])
                count = count + 1
            elif int(cost[COLUMNS['PULocationID']]) == obj["dropLocationId"] and int(cost[COLUMNS['DOLocationID']]) == obj["pickupLocationID"]:
                total_cost = total_cost + float(cost[COLUMNS['total_amount']])
                count = count + 1
        if(count!=0):
            avg_cost = total_cost/count
    return avg_cost
