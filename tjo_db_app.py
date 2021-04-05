# app.py
from flask import Flask, jsonify, request, render_template, session
import logging
from datetime import datetime, date
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from models import Lot, Bioburden, DoseAudit
from sqlalchemy import inspect, and_, or_
import json
import yagmail

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:XXXX@localhost:5432/ster_api"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# logging.basicConfig(filename="processor_info.log", filemode="w",
# level=logging.INFO)

# Declare auto option as BB
table = "BB"


@app.route("/")
def index():
    lots = Lot.query.all()
    bioburden = Bioburden.query.all()
    dose_audit = DoseAudit.query.all()
    return render_template("index.html", lots=lots, bb_reports=bioburden, da_reports=dose_audit)


@app.route('/table_choice', methods=["GET", "POST"])
def table_choice():
    global table
    jsdata = request.form.to_dict()
    table = jsdata['table']
    return table


@app.route('/request_help', methods=["POST"])
def request_help():
    topic = request.form.get("topic")
    help_request = request.form.get("help_request")
    print(f"Topic: {topic}; Request: {help_request}")
    # logging.warning(f"Topic: {topic}; Request: {help_request}")

    heading = "Thank you!"
    message = "Your request has been received :)"
    return render_template("error.html", heading=heading, message=message)


@app.route("/search_bb", methods=["POST"])
def search_bb():
    # can make Bioburden/the class be an input variable for this function
    # so that search can be separated for each db/tab
    bb_search_request = request.form.get("bb_report_id")

    if bb_search_request == "0":
        heading = "Sorry!"
        message = f"Choose a report."
        return render_template("error.html", heading=heading, message=message)

    packager = request.form.get("packager")
    start_date = request.form.get("report_start_date")
    end_date = request.form.get("report_end_date")

    # query db, get one row matching search
    if bb_search_request is not None:
        r = [Bioburden.query.get(bb_search_request)]

    # get all rows, returns list of objects
    if packager == "all":
        r = Bioburden.query.all()
    elif packager:
        # return lots with packager
        l = Lot.query.filter(Lot.packager == packager).all()
        # identify their lot numbers
        applicable_lot_numbers = [obj.lot_number for obj in l]
        # query bioburden corresponding to lot numbers
        r = Bioburden.query.filter(Bioburden.lot_id.in_(applicable_lot_numbers)).all()
    if not r:
        heading = "Sorry!"
        message = f"{packager} data hasn't been added yet."
        return render_template("error.html", heading=heading, message=message)

    if start_date or end_date:
        # return results between dates given
        if start_date is '': start_date = date(2000, 1, 1)
        if end_date is '': end_date = date.today()
        r = Bioburden.query.filter(and_(Bioburden.date >= start_date,
                                        Bioburden.date <= end_date)).all()

    # get table columns
    mapper_bioburden = inspect(Bioburden)
    mapper_lot = inspect(Lot)
    bb_column_headers = [column.key for column in mapper_bioburden.attrs]
    lot_column_headers = [column.key for column in mapper_lot.attrs]
    column_headers = lot_column_headers + bb_column_headers
    # match object/row to its info in the database
    master_r_list = []
    for obj in r:
        lot = Lot.query.filter(Lot.lot_number == obj.lot_id).first()
        # make this list automatically??
        r_list = [lot.id, lot.description, lot.part_number, lot.lot_number, lot.manufacturer,
                  lot.packager, lot.bioburden, obj.id, obj.lot_id, obj.date, obj.radiation_type, obj.aerobes, obj.fungi,
                  obj.recovery_est, obj.bioburden_est, obj.protocol, obj.test_report_num, obj.dose_audit_id]
        master_r_list.append(r_list)

    return render_template("search_results.html", headers=column_headers, r=master_r_list)


@app.route("/search_da", methods=["POST"])
def search_da():
    # can make Bioburden/the class be an input variable for this function
    # so that search can be separated for each db/tab
    da_search_request = request.form.get("da_report_id")

    if da_search_request == "0":
        heading = "Sorry!"
        message = f"Choose a report."
        return render_template("error.html", heading=heading, message=message)

    packager = request.form.get("packager")
    start_date = request.form.get("report_start_date")
    end_date = request.form.get("report_end_date")

    # query db, get one row matching search
    # before below meant a search by report, now returns even if on dose audit tab
    if da_search_request is not None:
        r = [DoseAudit.query.get(da_search_request)]

    # get all rows, returns list of objects
    if packager == "all":
        r = DoseAudit.query.all()
    elif packager:
        # return lots with packager
        l = Lot.query.filter(Lot.packager == packager).all()
        # identify their lot numbers
        applicable_lot_numbers = [obj.lot_number for obj in l]
        # query da corresponding to lot numbers
        r = DoseAudit.query.filter(DoseAudit.lot_id.in_(applicable_lot_numbers)).all()
    if not r:
        heading = "Sorry!"
        message = f"{packager} data hasn't been added yet."
        return render_template("error.html", heading=heading, message=message)

    if start_date or end_date:
        # return results between dates given
        if start_date is '': start_date = date(2000, 1, 1)
        if end_date is '': end_date = date.today()
        r = DoseAudit.query.filter(and_(DoseAudit.date >= start_date,
                                        DoseAudit.date <= end_date)).all()

    # get table columns
    mapper_da = inspect(DoseAudit)
    mapper_lot = inspect(Lot)
    da_column_headers = [column.key for column in mapper_da.attrs]
    lot_column_headers = [column.key for column in mapper_lot.attrs]
    column_headers = lot_column_headers + da_column_headers
    # match object/row to its info in the database
    master_r_list = []
    for obj in r:
        lot = Lot.query.filter(Lot.lot_number == obj.lot_id).first()
        # make this list automatically??
        r_list = [lot.id, lot.description, lot.part_number, lot.lot_number, lot.manufacturer,
                  lot.packager, lot.bioburden, obj.id, obj.date, obj.report, obj.lot_id, obj.sterility_test_date,
                  obj.target_dose, obj.min_dose, obj.max_dose, obj.num_positive, obj.num_samples]
        master_r_list.append(r_list)

    return render_template("search_results.html", headers=column_headers, r=master_r_list)


@app.route("/search", methods=["POST"])
def search():
    # Search can be separated for each db/tab
    packager = request.form.get("packager")
    start_date = request.form.get("report_start_date")
    end_date = request.form.get("report_end_date")

    # get all rows, returns list of objects
    if packager == "all":
        if table == "BB":
            r = Bioburden.query.all()
            if start_date or end_date:
                # return results between dates given
                if start_date is '': start_date = date(2000, 1, 1)
                if end_date is '': end_date = date.today()
                r = Bioburden.query.filter(and_(Bioburden.date >= start_date,
                                                Bioburden.date <= end_date)).all()
        elif table == "DA":
            r = DoseAudit.query.all()
            if start_date or end_date:
                # return results between dates given
                if start_date is '': start_date = date(2000, 1, 1)
                if end_date is '': end_date = date.today()
                r = DoseAudit.query.filter(and_(DoseAudit.date >= start_date,
                                                DoseAudit.date <= end_date)).all()
    elif packager:
        # return lots with packager
        l = Lot.query.filter(Lot.packager == packager).all()
        # identify their lot numbers
        applicable_lot_numbers = [obj.lot_number for obj in l]
        # query corresponding to lot numbers
        if table == "BB":
            r = Bioburden.query.filter(Bioburden.lot_id.in_(applicable_lot_numbers)).all()
            if start_date or end_date:
                # return results between dates given
                if start_date is '': start_date = date(2000, 1, 1)
                if end_date is '': end_date = date.today()
                r = Bioburden.query.filter(and_(Bioburden.lot_id.in_(applicable_lot_numbers),
                                                Bioburden.date >= start_date,
                                                Bioburden.date <= end_date)).all()
        elif table == "DA":
            r = DoseAudit.query.filter(DoseAudit.lot_id.in_(applicable_lot_numbers)).all()
            if start_date or end_date:
                # return results between dates given
                if start_date is '': start_date = date(2000, 1, 1)
                if end_date is '': end_date = date.today()
                r = DoseAudit.query.filter(and_(DoseAudit.lot_id.in_(applicable_lot_numbers),
                                                DoseAudit.date >= start_date,
                                                DoseAudit.date <= end_date)).all()

    if not r:
        heading = "Sorry!"
        message = f"Your search doesn't return any matching results."
        return render_template("error.html", heading=heading, message=message)

    # get table columns
    mapper_lot = inspect(Lot)
    lot_column_headers = [column.key for column in mapper_lot.attrs]
    if table == "BB":
        mapper_bb = inspect(Bioburden)
        bb_column_headers = [column.key for column in mapper_bb.attrs]
        column_headers = lot_column_headers + bb_column_headers
    elif table == "DA":
        mapper_da = inspect(DoseAudit)
        da_column_headers = [column.key for column in mapper_da.attrs]
        column_headers = lot_column_headers + da_column_headers

    # match object/row to its info in the database
    master_r_list = []
    if table == "BB":
        for obj in r:
            lot = Lot.query.filter(Lot.lot_number == obj.lot_id).first()
            # make this list automatically??
            r_list = [lot.id, lot.description, lot.part_number, lot.lot_number, lot.manufacturer, lot.packager,
                      lot.bioburden, obj.id, obj.lot_id, obj.date, obj.radiation_type, obj.aerobes, obj.fungi,
                      obj.recovery_est, obj.bioburden_est, obj.protocol, obj.test_report_num, obj.dose_audit_id]
            master_r_list.append(r_list)
    elif table == "DA":
        for obj in r:
            lot = Lot.query.filter(Lot.lot_number == obj.lot_id).first()
            # make this list automatically??
            r_list = [lot.id, lot.description, lot.part_number, lot.lot_number, lot.manufacturer,
                      lot.packager, lot.bioburden, obj.id, obj.date, obj.report, obj.lot_id, obj.sterility_test_date,
                      obj.target_dose, obj.min_dose, obj.max_dose, obj.num_positive, obj.num_samples]
            master_r_list.append(r_list)

    return render_template("search_results.html", headers=column_headers, r=master_r_list)


@app.route("/search_page")
def search_page():
    return render_template("search_page.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/help")
def help():
    return render_template("help.html")


@app.route("/add_data", methods=["POST"])
def add_data():
    """Add to the database."""

    # Get form information from html.
    name = request.form.get("name")
    try:
        flight_id = int(request.form.get("flight_id"))
    except ValueError:
        return render_template("error.html", message="Invalid input.")

    # Make sure the flight exists.
    flight = Flight.query.get(flight_id)
    if not flight:
        return render_template("error.html", message="No such input with that id.")

    # Add passenger.
    flight.add_passenger(name)
    return render_template("success.html")


if __name__ == "__main__":
    # app.run(host="127.0.0.1", debug=True)
    app.run(host="0.0.0.0")
