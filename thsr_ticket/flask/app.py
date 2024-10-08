import sys
import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from tinydb import TinyDB

sys.path.append(os.getcwd())
print(sys.path)
from thsr_ticket.controller.web_flow import WebFlow
from thsr_ticket.configs.web.enums import StationMapping
from thsr_ticket.configs.common import AVAILABLE_TIME_TABLE
from thsr_ticket.model.db import RecordFirstPage, RecordTrainPage, RecordTicketPage
from thsr_ticket.remote.http_request import HTTPRequest

app = Flask(__name__)

db = TinyDB("thsr_ticket/.db/history.json")
flow = None
client = None
record = None


@app.route("/reserve/step1", methods=["GET", "POST"])
def reserve_step1():
    if request.method == "POST":
        global flow
        flow = WebFlow()
        record = RecordFirstPage()
        record.start_station = request.form.get("start_station", 2)  # 預設值為 2
        record.dest_station = request.form.get("dest_station", 2)  # 預設值為 2
        record.outbound_date = request.form.get("travel_date")
        record.outbound_time = request.form.get("travel_time")
        record.adult_num = request.form.get("adult_num")
        if flow.new_flow(record):
            print("BookingFlow instance created")
            return redirect(url_for("reserve_step2"))
        else:
            print("Fail")
            return jsonify({"message": "Failed to create new flow"}), 400
    stations = StationMapping
    return render_template(
        "reserve.html", stations=stations, available_times=AVAILABLE_TIME_TABLE
    )


@app.route("/reserve/step2", methods=["GET", "POST"])
def reserve_step2():
    global flow
    if request.method == "POST":
        record = RecordTrainPage()
        record.selection_time = request.form.get("selection_time")
        if flow.train_page(record):
            return redirect(url_for("reserve_step3"))
        else:
            return jsonify({"message": "Failed to select train"}), 400
    return render_template("reserve2.html", stations=flow.get_train_list())


@app.route("/reserve/step3", methods=["GET", "POST"])
def reserve_step3():
    global flow
    num =3
    if request.method == "POST":
        record = RecordTicketPage()
        record.personal_id = [request.form.get(f'personal_id_{i}') for i in range(num)]
        record.phone = request.form.get("phone")
        record.email = request.form.get("email")
        if flow.ticket_page(record):
            return redirect(url_for("reserve_step4"))
        else:
            return jsonify({"message": "Failed to select train"}), 400
    return render_template("reserve3.html", num=num)


@app.route("/reserve/step4", methods=["GET"])
def reserve_step4():
    global flow
    return render_template("reserve4.html", sucess=flow.get_result())


@app.route("/api/data", methods=["GET"])
def get_data():
    data = db.all()
    return jsonify(data), 200


@app.route("/show_db", methods=["GET"])
def show_db():
    return render_template("show_db.html")


if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
