import os
import requests
from datetime import date
from wwo_hist import retrieve_hist_data
from data_preprocessing import preprocessing
from windDir_NN import windDir
from windSpeed_SVR import windSpeed

api_key = 'dae5811250aa4cdd9db101705202903'
start_date = '01-JUL-2008'
end_date = date.today().strftime("%d-%b-%Y").upper()
frequency= 24

url = 'http://api.worldweatheronline.com/premium/v1/weather.ashx?'

params = {
    'key': api_key,
    'num_of_days': '1',
    'tp': '24',
    'cc': 'no',
    'mca': 'no',
    'format': 'json',
    'includelocation': 'yes',
    'q': None,
    'date': None,
    }

def getHistoricalData(location):
    retrieve_hist_data(api_key, [location], start_date, end_date, frequency, location_label = False, export_csv = True, store_df = False)

location = '21.238611,73.350000'
getHistoricalData(location)

preprocessing(location)
print("Preprocessing completed!")

print("Predicting wind direction...")
windDir(location)
print("Wind direction prediction completed!")

print("Predicting wind speed...")
windSpeed(location)
print("Wind speed prediction completed!")