from flask import Flask, render_template
from pyScripts.demos import simulate_plume_model
import datetime

app = Flask(__name__, static_folder='static')


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/", methods=['POST'])
def disp_output():
    # lat = input("Enter lat: ")
    # lng = input("Enter lng: ")
    # day = int(input("Enter Day: "))
    # month = int(input("Enter Month: "))
    # year = int(input("Enter Year: "))
    # latLng = lat + ',' + lng  # '19.0368,73.0158'

    latLng = '19.0368,73.0158'
    day = 1
    month = 2
    year = 2020

    fig, ax, anim = simulate_plume_model(
        latLng=latLng, start_datetimeObject=datetime.datetime(year, month, day))
    anim_path = 'static/simulation.mp4'

    return render_template('index.html', output_path=anim_path)


if __name__ == "__main__":
    app.run()
