from flask import Flask, render_template, request
from pyScripts.demos import simulate_plume_model
import datetime
import os
from os import path

app = Flask(__name__, static_folder='static')
anim_path = 'static\simulation.mp4'


@app.route("/")
def index():
    return render_template('index.html', visibility="hidden")


@app.route("/", methods=['POST'])
def disp_output():
    loc = request.form['inputLoc']
    loc_lat = request.form['locLat']
    loc_lng = request.form['locLng']

    latLng = loc_lat+','+loc_lng
    print(latLng)
    # latLng = '21.238611,73.350000'  # Best Case
    # latLng = '19.033000,73.029700'  # Worst Case
    day = 2
    month = 4
    year = 2020

    # fig, ax, anim = simulate_plume_model(
    #     latLng=latLng, start_datetimeObject=datetime.datetime(year, month, day))

    return render_template('index.html', output_path=anim_path, visibility="visible")


if __name__ == "__main__":
    # if path.exists(anim_path):
    #     os.remove(anim_path)
    app.run()
