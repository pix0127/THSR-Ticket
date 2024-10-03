from flask import Flask, jsonify, render_template, request
from tinydb import TinyDB
from controller.booking_flow import BookingFlow

app = Flask(__name__)

db = TinyDB("../thsr_ticket/.db/history.json")
flow = None

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    global flow
    if request.method == 'POST':
        start_station = request.form.get('start_station', 2)  # 預設值為 2
        flow = BookingFlow()
        result = flow.add_new_reserve(start_station)
        return jsonify({"message": result}), 200
    return render_template('reserve.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    data = db.all()
    return jsonify(data), 200

@app.route('/show_db', methods=['GET'])
def show_db():
    return render_template('show_db.html')

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)