import os
import csv
import requests
import datetime
from datetime import date
from wwo_hist import retrieve_hist_data
import csv
from pyScripts.mlModels.data_collection import collect


def getApiKey():
    # api_list = [['sifisel996@mailboxt.com', '8a8a662e947c4d8bb7a95716200104'],
    #             ['noceb41307@mailboxt.com', '77d172a5ab384b0b889100954200104'],
    #             ['rirake5230@smlmail.com',  'cced7653c5684a619c2101325200104'],
    #             ['yiwov98027@mailboxt.com', 'd230320c4282460580d101501200104'],
    #             ['locohed521@svpmail.com',  'ae8cb3f0c32b4b8e9d3101615200104']]
    api_list = [['sifisel996@mailboxt.com', '78dec329952f4b7387972337200104'],
                ['noceb41307@mailboxt.com', '78dec329952f4b7387972337200104'],
                ['rirake5230@smlmail.com',  '78dec329952f4b7387972337200104'],
                ['yiwov98027@mailboxt.com', '78dec329952f4b7387972337200104'],
                ['locohed521@svpmail.com',  '78dec329952f4b7387972337200104']]
    counterFile = open('.\dataFiles\counter.txt', 'r+')
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
    #roadmap, satellite, terrain, hybrid
    response = requests.get(URL)
    fileLocation = "static\map.png"
    with open(fileLocation, 'wb') as imageFile:
        imageFile.write(response.content)


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
    getMap(location)
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
    return(apiList, location)

# getMap('37.4245,141.0298')
