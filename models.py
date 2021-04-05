# create_postgres_db.py
from flask import Flask, jsonify, request, render_template, session
import logging
from datetime import datetime
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:XXXX@localhost:5432/ster_api"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Initialize db connection
db = SQLAlchemy(app)
# Initialize db migration management
migrate = Migrate(app, db)


class Lot(db.Model):
    __tablename__ = "lots"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    part_number = db.Column(db.String, nullable=False)
    lot_number = db.Column(db.String, nullable=False, unique=True)
    manufacturer = db.Column(db.String, nullable=False)
    packager = db.Column(db.String, nullable=False)
    bioburden = db.Column(db.Integer, nullable=True)

    def __init__(self, description, part_number, lot_number,
                 manufacturer, packager):
        self.description = description
        self.part_number = part_number
        self.lot_number = lot_number
        self.manufacturer = manufacturer
        self.packager = packager

    def __repr__(self):
        return f"<Lot {self.lot_number}>"


class Bioburden(db.Model):
    __tablename__ = 'bioburden'

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.String, db.ForeignKey("lots.lot_number"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    radiation_type = db.Column(db.String, nullable=False)
    aerobes = db.Column(db.String, nullable=False)
    fungi = db.Column(db.String, nullable=False)
    recovery_est = db.Column(db.String, nullable=False)
    bioburden_est = db.Column(db.String, nullable=False)
    protocol = db.Column(db.String, nullable=False)
    test_report_num = db.Column(db.String, nullable=False)
    dose_audit_id = db.Column(db.Integer, nullable=True)

    def __init__(self, lot_id, date, radiation_type, aerobes, fungi, recovery_est, bb_est,
                 protocol, test_report):
        self.lot_id = lot_id
        self.date = date
        self.radiation_type = radiation_type
        self.aerobes = aerobes
        self.fungi = fungi
        self.recovery_est = recovery_est
        self.bioburden_est = bb_est
        self.protocol = protocol
        self.test_report_num = test_report

    def __repr__(self):
        return f"<Bioburden {self.test_report_num}>"


class DoseAudit(db.Model):
    __tablename__ = 'dose_audit'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    report = db.Column(db.String, nullable=False)
    lot_id = db.Column(db.String, nullable=False)
    sterility_test_date = db.Column(db.Date, nullable=False)
    target_dose = db.Column(db.String, nullable=False)
    min_dose = db.Column(db.String, nullable=False)
    max_dose = db.Column(db.String, nullable=False)
    num_positive = db.Column(db.Integer, nullable=False)
    num_samples = db.Column(db.Integer, nullable=False)

    def __init__(self, date, report, lot_id, sterility_date, target_dose,
                 min_dose, max_dose, num_positive, num_samples):
        self.date = date
        self.report = report
        self.lot_id = lot_id
        self.sterility_test_date = sterility_date
        self.target_dose = target_dose
        self.min_dose = min_dose
        self.max_dose = max_dose
        self.num_positive = num_positive
        self.num_samples = num_samples

    def __repr__(self):
        return f"<Dose Audit {self.report}>"


def print_ok():
    print("Models imported")


if __name__ == '__main__':
    print_ok()
