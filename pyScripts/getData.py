import os
import csv
import requests
import datetime
from datetime import date
from wwo_hist import retrieve_hist_data
import csv
from pyScripts.mlModels.data_collection import collect

def getData(location, startDate):
    filename = location+".csv"
    filepath = "dataFiles/"+filename
    if os.path.exists(filepath) == False:
        collect(location)

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