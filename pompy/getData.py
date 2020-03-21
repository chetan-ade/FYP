import os
import csv
import requests
import datetime
from datetime import date
from wwo_hist import retrieve_hist_data

api_key = '91a5c7d65b78493086651634202801'
start_date = '01-JUL-2008'
end_date = date.today().strftime("%d-%b-%Y").upper()
frequency = 24

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


def getHistoricalData(location, start_date, end_date):
    hist_weather_data = retrieve_hist_data(api_key, [
                                           location], start_date, end_date, frequency, location_label=False, export_csv=False, store_df=True)


def getPredictedData(location):
    apiList = []
    params['q'] = location
    for i in range(16):
        curDate = (datetime.datetime.today() +
                   datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        params['date'] = curDate
        r = requests.get(url=url, params=params)
        dataJson = r.json()
        location = dataJson['data']['nearest_area'][0]['areaName'][0]['value']
        curDir = dataJson['data']['weather'][0]['hourly'][0]['winddirDegree']
        curSpd = dataJson['data']['weather'][0]['hourly'][0]['windspeedKmph']
        element = {'Date': curDate, 'Direction': curDir, 'Speed': curSpd}
        apiList.append(element)
    return (apiList, location)


getHistoricalData('Mumbai', '01-JAN-2020', '16-JAN-2020')
