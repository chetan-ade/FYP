import os
import csv
import requests
import datetime
from datetime import date
from wwo_hist import retrieve_hist_data

# PATH TO SAVE CSV FILE
# os.chdir("/content")

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


def getHistoricalData(location):
    hist_weather_data = retrieve_hist_data(api_key, [
                                           location], start_date, end_date, frequency, location_label=False, export_csv=True, store_df=False)


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
    # print(location)
    # print(apiList)
    return (apiList, location)


def listToCSV(dataList, csv_file):
    csv_columns = ['Date', 'Direction', 'Speed']
    # csv_file = "PredictedFromAPI.csv"
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dataList:
                writer.writerow(data)
    except IOError:
        print("Error while creating", csv_file)


def createWindList(apiList, modelList):
    windList = []
    for i in range(len(apiList)):
        Date = apiList[i]['Date']
        Direction = (int(apiList[i]['Direction']) +
                     int(modelList[i]['Direction']))/2
        Speed = (int(apiList[i]['Speed']) + int(modelList[i]['Speed']))/2
        windList.append({'Date': Date, 'Direction': str(
            Direction), 'Speed': str(Speed)})
    print(windList)


# apiList, location = getPredictedData('19.0368,73.0158')
