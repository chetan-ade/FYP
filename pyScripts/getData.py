import os
import csv
import requests
import datetime
from datetime import date
from wwo_hist import retrieve_hist_data
import csv
from pyScripts.mlModels.data_collection import collect

api_key = 'ca38a817c48d4240beb84742200104'

url = 'http://api.worldweatheronline.com/premium/v1/weather.ashx?'

parameters = {
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


def getLocationName(location):
    parameters['q'] = location
    curDate = (datetime.datetime.today()).strftime('%Y-%m-%d')
    parameters['date'] = curDate
    r = requests.get(url=url, params=parameters)
    dataJson = r.json()
    locationName = dataJson['data']['nearest_area'][0]['areaName'][0]['value']
    return locationName


def getData(location, startDate):
    locationName = getLocationName(location)
    filename = locationName+".csv"
    filepath = "dataFiles/"+filename
    if os.path.exists(filepath) == False:
        collect(location, api_key)
        os.rename('dataFiles/'+location+'.csv', filepath)

    # datetimeobject = datetime.datetime.strptime(startDate,"%d-%b-%Y")
    startDateStr = startDate.strftime("%Y-%m-%d")

    csvList = []
    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            csvList.append(row)

    for i in range(len(csvList)):
        if csvList[i][0] == startDateStr:
            finalList = csvList[i:i+15]

    apiList = []
    for i in finalList:
        curDate = i[0]
        curDir = i[-2]
        curSpd = i[-1]
        element = {'Date': curDate, 'Direction': curDir, 'Speed': curSpd}
        apiList.append(element)

    # print(apiList)
    return(apiList, location)

# getData('21.238611,73.350000', '15-Jan-2020')
