import os
import csv
import requests
import datetime
from datetime import date
from wwo_hist import retrieve_hist_data
from scripts.mlModels.data_collection import collect


def getApiKey():
    api_list = [['weyeja9517@mailpkc.com', '3b460d8274364b33834151048201109'],
                ['nejikox587@maileze.net', '9628cc3a00c249af860155134201109'],
                ['cofox88589@mailpkc.com', '06802087188d44ab801155234201109'],
                ['newig78670@mailetk.com', '477eb8464e8e45528a2155608201109'],
                ['sayaka8725@oramail.net', 'd99a804d24d74b6795f160457201109']]

    counterFile = open('.\data\others\counter.txt', 'r+')
    counter = int(counterFile.read())

    counterFile.seek(0)
    counterFile.write(str((counter+1) % len(api_list)))

    return api_list[counter][1]


api_key = getApiKey()

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


def getMap(location):
    google_maps_api_key = "AIzaSyAqpHfAhTZPkSXc3Bs6dskNBv-GXIVOa2I"

    ZOOM = 4

    URL = "https://maps.googleapis.com/maps/api/staticmap?" + "center=" + \
        location + "&zoom=" + str(ZOOM) + "&scale=2" + "&maptype=roadmap"+"&size=640x320 " + \
        "&key=" + google_maps_api_key

    response = requests.get(URL)
    fileLocation = "static\images\map.png"

    with open(fileLocation, 'wb') as imageFile:
        imageFile.write(response.content)


def getLocationName(location):
    parameters['q'] = location

    curDate = (datetime.datetime.today()).strftime('%Y-%m-%d')
    parameters['date'] = curDate

    r = requests.get(url=url, params=parameters)

    dataJson = r.json()

    try:
        locationName = dataJson['data']['nearest_area'][0]['areaName'][0]['value']
    except:
        print("\n\n\nAPI not online...\nPress Ctrl + C to exit.\n\n\n")
        exit()

    return locationName


def getData(location, startDate):
    locationName = getLocationName(location)
    getMap(location)

    filename = locationName+".csv"
    filepath = "data/"+filename

    if os.path.exists(filepath) == False:
        collect(location, api_key)
        os.rename('data/'+location+'.csv', filepath)
    else:
        print("CSV File already present.")

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

    return(apiList, location)
