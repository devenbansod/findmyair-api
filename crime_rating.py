from math import cos, asin, sqrt
import pandas as pd
import numpy as np
from os import path
import gc
def distance(lat1, lon1, nlat2, nlon2):
    p = 0.017453292519943295     
    a = 0.5 - np.cos((nlat2 - lat1) * p)/2 + np.cos(lat1 * p) * np.cos(nlat2 * p) * (1 - np.cos((nlon2 - lon1) * p)) / 2
    return 12742 * np.arcsin(np.sqrt(a)) 


def compute_pairwise_distance(airbnb_dataset, crime_dataset):

    num_airbnb = airbnb_dataset.shape[0]
    # num_crimes = crime_dataset.shape[0]

    distance_matrix = np.zeros((airbnb_dataset.shape[0], crime_dataset.shape[0]))

    if path.exists("data/distance_matrix.npy"):
        print ("Cached file found")
        distance_matrix = np.load("data/distance_matrix.npy",mmap_mode='r+')
        return distance_matrix

    for i in range(num_airbnb):
        if i%500 == 0:
            print ("\r",i,"/",num_airbnb,end="")
            gc.collect()
        airbnb_lat  = airbnb_dataset['latitude'][i]
        airbnb_long = airbnb_dataset['longitude'][i]
        
        crime_lat = crime_dataset['Latitude'][:]
        crime_long = crime_dataset['Longitude'][:]

        distance_matrix[i,:] = distance(airbnb_lat,airbnb_long, crime_lat, crime_long)
        
    np.save("data/distance_matrix.npy",distance_matrix)
    return distance_matrix

def crime_score(crime_weight, distance_matrix):

    num_airbnb = distance_matrix.shape[0]
    crime_score = np.zeros(num_airbnb)

    for i in range(num_airbnb):
        crime_score[i] = np.sum(crime_weight[np.where(distance_matrix[i,:] <= 2)]) + (0.5 * np.sum(crime_weight[np.where((distance_matrix[i,:] < 5) & (distance_matrix[i,:] > 2))]))

    return crime_score

def set_weight(crime_dataset):

    crime_type = np.array(crime_dataset['LAW_CAT_CD'])
    crime_weight = np.zeros(len(crime_type))
    
    crime_weight[crime_type == 'VIOLATION'] = 0.2
    crime_weight[crime_type == 'MISDEMEANOR'] = 0.3
    crime_weight[crime_type == 'FELONY'] = 0.5

    return crime_weight

if __name__ == "__main__":
    #Import data here

    airbnb_dataset = pd.read_csv('data/listings-filtered.csv')
    crime_dataset = pd.read_csv('data/crime_rate_filtered.csv')

    crime_weight = set_weight(crime_dataset)

    distance_matrix = compute_pairwise_distance(airbnb_dataset, crime_dataset)

    crime_scores = crime_score(crime_weight, distance_matrix)

    # np.save("crime_scores", crime_scores)
    print (np.argmin(crime_score))
    
    