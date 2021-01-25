import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Calculate year prior date for use in precipitation route


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f'Welcome to the Weather Site</br>'
        f'Available Routes: </br>'
        f'/api/v1.0/precipitation</br>'
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/start</br>"
        f"/api/v1.0/start/end</br>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
# Create our session (link) from Python to the DB
    session = Session(engine)
    recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent = dt.datetime.strptime(recent[0],'%Y-%m-%d')
    year_prior = dt.date(most_recent.year - 1, most_recent.month, most_recent.day)
    # Query all results of prcp
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_prior).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    all_precip = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_precip.append(prcp_dict)
    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
# Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all results
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    results = session.query(*sel).all()

    session.close()

    # Create a dictionary from the row data and append to a list stations
    stations = []
    for station, name, latitude, longitude, elevation in results:
        stat_dict = {}
        stat_dict["station"] = station
        stat_dict["name"] = name
        stat_dict["latitude"] = latitude
        stat_dict["longitude"] = longitude
        stat_dict["elevation"] = elevation
        stations.append(stat_dict)
    return jsonify(stations)
@app.route("/api/v1.0/tobs")
def tobs():
# Create our session (link) from Python to the DB
    session = Session(engine)
    recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent = dt.datetime.strptime(recent[0],'%Y-%m-%d')
    year_prior = dt.date(most_recent.year - 1, most_recent.month, most_recent.day)
    sel2 = [Measurement.station, func.count(Measurement.id)]
    stat_count = session.query(*sel2).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).all()
    # Query all results of tobs
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_prior).filter(Measurement.station == stat_count[0][0]).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)
    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def climatedata(start):
# Create our session (link) from Python to the DB
    session = Session(engine)
    start_date = dt.datetime.strptime(start,'%Y-%m-%d')
    t = Measurement.tobs
    temps = [func.min(t), func.max(t), func.avg(t)]
    temp_stats = session.query(*temps).filter(Measurement.date >= start_date).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    all_tobs = []
    for tmin, tmax, tavg in temp_stats:
        tobs_dict = {}
        tobs_dict["TMIN"] = tmin
        tobs_dict["TAVG"] = tavg
        tobs_dict["TMAX"] = tmax
        all_tobs.append(tobs_dict)
    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>/<end>")
def climatestartend(start, end):
# Create our session (link) from Python to the DB
    session = Session(engine)
    start_date = dt.datetime.strptime(start,'%Y-%m-%d')
    end_date = dt.datetime.strptime(end,'%Y-%m-%d')
    t = Measurement.tobs
    temps = [func.min(t), func.max(t), func.avg(t)]
    temp_stats = session.query(*temps).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Create a dictionary from the row data and append to a list
    all_tobs = []
    for tmin, tmax, tavg in temp_stats:
        tobs_dict = {}
        tobs_dict["TMIN"] = tmin
        tobs_dict["TAVG"] = tavg
        tobs_dict["TMAX"] = tmax
        all_tobs.append(tobs_dict)
    return jsonify(all_tobs)

if __name__ == '__main__':
    app.run(debug=True)
