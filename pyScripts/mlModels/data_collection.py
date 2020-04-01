import os
import requests
from datetime import date
from wwo_hist import retrieve_hist_data
from pyScripts.mlModels.data_preprocessing import preprocessing
from pyScripts.mlModels.windDir_NN import windDir
from pyScripts.mlModels.windSpeed_SVR import windSpeed


def collect(location, api_key):
    api_key = api_key
    start_date = '01-JUL-2008'
    end_date = date.today().strftime("%d-%b-%Y").upper()
    frequency = 24

    def getHistoricalData(location):
        retrieve_hist_data(api_key, [location], start_date, end_date,
                           frequency, location_label=False, export_csv=True, store_df=False)

    # location = '21.238611,73.350000'
    getHistoricalData(location)

    preprocessing(location)
    print("Preprocessing completed!")

    print("Predicting wind direction...")
    windDir(location)
    print("Wind direction prediction completed!")

    print("Predicting wind speed...")
    windSpeed(location)
    print("Wind speed prediction completed!")
