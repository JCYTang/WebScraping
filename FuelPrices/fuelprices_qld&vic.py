import json
import requests
import pandas as pd
import csv
import os
from datetime import datetime

#open up postcodes file with latitude and longitude co-ordinates
#feed parameters into petrolspy api
#only grab the prices where the relevant tag is true

postcodes_file = 'postcodes_latlng.csv'
url = 'https://petrolspy.com.au/webservice-1/station/box'
parameters = {}
stations = []
prices = []
date = datetime.today().strftime('%Y-%m-%d')

with open(postcodes_file, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter = ',')
    next(reader)
    for row in reader:
        parameters['neLat'] = row[3]
        parameters['neLng'] = row[4]
        parameters['swLat'] = row[5]
        parameters['swLng'] = row[6]

        response = requests.get(url, params=parameters)
        data = response.json()
        print(data)
        if list(data['message'].keys())[0] != 'error':
            for station in data['message']['list']:
                print(row[3], row[4], row[5], row[6], station)

                id = station.get('id')
                brand = station.get('brand')
                name = station.get('name')
                address = station.get('address')
                suburb = station.get('suburb')
                state = station.get('state')
                postcode = station.get('postCode')

                #only consider prices where relevant key is true and the state is qld or vic
                if state == 'QLD' or state == 'VIC':
                    stations.append([id, brand, name, address, suburb, state, postcode])
                    for type in station['prices']:
                        if station['prices'][type]['relevant']:
                            fueltype = station['prices'][type].get('type')
                            price = float(station['prices'][type].get('amount'))
                            print([id, name, brand, state, suburb, address, postcode, fueltype, price])
                            prices.append([date, id, fueltype, price])

    df_stations = pd.DataFrame(stations, columns=['id', 'brand', 'name', 'address', 'suburb', 'state', 'postcode'])
    df_stations = df_stations.drop_duplicates()

    df_prices = pd.DataFrame(prices, columns=['date', 'id', 'fueltype', 'price'])
    df_prices = df_prices.drop_duplicates()

    # save data as csv file
    archive_folder = 'W:\RESEARCH\Personal Folders\Jeremy\WebScraping\FuelPrices\Archive'
    df_stations.to_csv(os.path.join(archive_folder, 'fuelstations_qld&vic.csv'), index=False)
    df_prices.to_csv(os.path.join(archive_folder, 'fuelprices_qld&vic_' + datetime.today().strftime('%Y%m%d') + '.csv'), \
        index=False)