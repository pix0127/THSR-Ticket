import sys
import os
from flask import Flask, jsonify, render_template, request
from tinydb import TinyDB

sys.path.append(os.getcwd())
print(sys.path)
from thsr_ticket.controller.booking_flow import BookingFlow
from thsr_ticket.configs.web.enums import StationMapping
from thsr_ticket.configs.web.param_schema import BookingModel
from thsr_ticket.configs.common import (
    AVAILABLE_TIME_TABLE
)

app = Flask(__name__)

db = TinyDB("thsr_ticket/.db/history.json")
flow = None

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    global flow
    if request.method == 'POST':
        start_station = request.form.get('start_station', 2)  # 預設值為 2
        dest_station = request.form.get('dest_station', 2)  # 預設值為 2
        travel_date = request.form.get('travel_date')
        book_model = BookingModel(
            start_station=start_station,
            dest_station=dest_station,
            outbound_date=travel_date,
        )
        flow = BookingFlow()
        #result = flow.add_new_reserve(start_station)
        return jsonify({"message": start_station}), 200
    stations = StationMapping
    return render_template('reserve.html', stations=stations, available_times=AVAILABLE_TIME_TABLE)

@app.route('/api/data', methods=['GET'])
def get_data():
    data = db.all()
    return jsonify(data), 200

@app.route('/show_db', methods=['GET'])
def show_db():
    return render_template('show_db.html')

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)