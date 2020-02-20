from flask import Flask, jsonify
from scipy import stats
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func


# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)
# Database Setup

app = Flask(__name__)

@app.route("/")
def index():
    print("---Index selected.---")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/(start date) - Enter valid date (Year-Month-Day)<br/>"
        f"/api/v1.0/(start date)/(end date) - Enter valid start and end date (Year-Month-Day)<br/>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("---Precipitation selected.---")
    dates = session.query(Measurement).order_by(Measurement.date.desc())
    session.close()
    count = 0
    year_dates = []
    year_prcp = []
    for date in dates:
        date_new = date.date
        date_new = datetime.strptime(date_new, "%Y-%m-%d")
        if count==0:
            end_date = date_new - relativedelta(months=+12)
            count+=1
        if date_new >= end_date:
            if(date.prcp != None):
                year_prcp.append(date.prcp)
                year_dates.append(date.date)
    pdict = {"Date":year_dates, "Precipitation": year_prcp}
    return jsonify(pdict)

@app.route("/api/v1.0/stations")
def stations():
    print("---Stations selected.---")
    stations_data = session.query(Station.name).order_by(Station.name.desc()).all()
    stations_data = [stations_data[0] for stations_data in stations_data]
    session.close()
    return jsonify(stations_data)

@app.route("/api/v1.0/tobs")
def tobs():
    print("---Temperature (tobs) selected.---")
    temp_query_date = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).all()
    temp_query_date = [temp_query_date[0] for temp_query_date in temp_query_date]
    temp_query_dates = datetime.strptime(temp_query_date[0], "%Y-%m-%d")
    #==========Get most recent date and format it======

    #query
    temp_query = session.query(Measurement.tobs).\
        filter(Measurement.date >= (temp_query_dates - dt.timedelta(days=365))).all()
    temp_query = [temp_query[0] for temp_query in temp_query]
    session.close()
    return jsonify(temp_query)

@app.route("/api/v1.0/<start>")
def start_date(start):
    print("---Start date selected.---")
    try:
        dates = session.query(Measurement.date).all()
        dates = [dates[0] for dates in dates]
        if start in dates:
                start_date_query = session.query(Measurement.tobs).\
                    filter(Measurement.date >= (start)).all()
                start_date_query = [start_date_query[0] for start_date_query in start_date_query]
                session.close()
                average = round(sum(start_date_query) / len(start_date_query),1)
                return jsonify(f"Minimum : {min(start_date_query)}",
                    f"Average : {average}",
                    f"Maximum : {max(start_date_query)}")
        else:
            session.close()
            return jsonify({"1error": f"This date, {start}, is not in the correct format or is outside the scope of this database. Please enter a valid date in the correct format: Year-Month-Day."}), 404
    except:
        session.close()
        return jsonify({"2error": f"This date, {start}, is not in the correct format. Please enter a valid date in the correct format: Year-Month-Day."}), 404
    
@app.route("/api/v1.0/<start>/<end>")
def start_and_end_date(start,end):
    print("---Start and end date selected.---")
    
    ###### DATE FORMAT TEST

    #test to make sure the start date is in the correct date format
    start_test = False
    try:
        start = datetime.strptime(start, "%Y-%m-%d")
        if 'datetime.datetime' in str(type(start)):
            start_test = True
    except:
        return jsonify({"error": f"This START date, {start}, is not in the correct format. Please enter a valid date in the correct format: Year-Month-Day."}), 404

    #test to make sure the end date is in the correct date format
    end_test = False
    try:
        end = datetime.strptime(end, "%Y-%m-%d")
        if 'datetime.datetime' in str(type(end)):
            end_test = True
    except:
        return jsonify({"error": f"This END date, {end}, is not in the correct format. Please enter a valid date in the correct format: Year-Month-Day."}), 404

    ######## DATE FORMAT TEST
    
    start1 = str(start.date())
    end1 = str(end.date())

    if end_test and start_test == True:
        if end > start:
            dates = session.query(Measurement.date).all()
            dates = [dates[0] for dates in dates]
            if start1 and end1 in dates:
                    start_date_query = session.query(Measurement.tobs).\
                        filter(Measurement.date >= (start), Measurement.date <= (end)).all()
                    start_date_query = [start_date_query[0] for start_date_query in start_date_query]
                    session.close()
                    average = round(sum(start_date_query) / len(start_date_query),1)
                    return jsonify(f"Minimum : {min(start_date_query)}",
                        f"Average : {average}",
                        f"Maximum : {max(start_date_query)}")
            else:
                session.close()
                return jsonify({"error": f"One of the dates enterd is outside the scope of this database."}), 404
        else:
            session.close()
            return jsonify({"error": f"End date is less than the start date. Please enter an end date greater than the start date"}), 404

if __name__ == "__main__":
    app.run(debug=True)