import os
import csv
import requests
import datetime
from datetime import date
from wwo_hist import retrieve_hist_data
from scripts.mlModels.data_collection import collect


def getApiKey():
    api_list = [['speceki7301@agilekz.com', '306a1403311b490f8fa84305201406'],
                ['xodaxox367@lefaqr5.com', 'd300f1d21fef42148e384613201406'],
                ['wamot13082@klefv.com',  '6bd90d5cf75a462f83984731201406'],
                ['voyamo7768@klefv.com', '9b4f0330bcc14d9b92484903201406'],
                ['xefic38903@bewedfv.com',  'f6d2dd151cd84a4eb3b85116201406']]

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
