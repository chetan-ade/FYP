import os
import csv
import requests
import datetime
from datetime import date
from wwo_hist import retrieve_hist_data
import csv

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
    return (apiList, location)


def getData(location, startDate):
    today = datetime.datetime.today()
    apiList = []
    fileCreated = False
    diff = today.date()-startDate.date()
    if (startDate.date() == today.date()):
        apiList, tempLocation = getPredictedData(location)
    elif(diff >= datetime.timedelta(days=15)):
        startDateStr = startDate.strftime("%d-%b-%Y").upper()
        endDate = startDate + datetime.timedelta(days=16)
        endDateStr = endDate.strftime("%d-%b-%Y").upper()
        getHistoricalData(location, startDateStr, endDateStr)

        csvList = []
        filename = location+".csv"
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                csvList.append(row)
        csvList = csvList[1:17]
        for i in csvList:
            curDate = i[0]
            curDir = i[-2]
            curSpd = i[-1]
            element = {'Date': curDate, 'Direction': curDir, 'Speed': curSpd}
            apiList.append(element)
        fileCreated = True
    else:
        startDateStr = startDate.strftime("%d-%b-%Y").upper()
        endDate = datetime.datetime.today()
        endDateStr = endDate.strftime("%d-%b-%Y").upper()
        getHistoricalData(location, startDateStr, endDateStr)
        csvList = []
        filename = location+".csv"
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                csvList.append(row)
        csvList = csvList[1:((endDate-startDate).days)+1]
        for i in csvList:
            curDate = i[0]
            curDir = i[-2]
            curSpd = i[-1]
            element = {'Date': curDate, 'Direction': curDir, 'Speed': curSpd}
            apiList.append(element)
        tempList, tempLoc = getPredictedData(location)
        apiList.extend(tempList)
        apiList = apiList[:16]
        fileCreated = True
    if fileCreated:
        filename = location+".csv"
        os.remove(filename)
    return(apiList, location)
