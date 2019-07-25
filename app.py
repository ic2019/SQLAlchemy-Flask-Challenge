# Importing all dependencies
import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import and_

from flask import Flask, jsonify, redirect


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

# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"<h1>Welcome to Climate API</h1><br/>"
        f"<hr>"
        f"<h2>Available Routes:</h2>"
        f"<p>Usage Example: <em>localhost:5000/api/v1.0/precipitation</em><p>"
        f"<h3>1. /api/v1.0/precipitation</h3>"
        f"<p>Usage Example: <em>localhost:5000/api/v1.0/stations</em><p>"
        f"<h3>2. /api/v1.0/stations</h3>"
        f"<p>Usage Example: <em>localhost:5000/api/v1.0/tobs</em><p>"
        f"<h3>3. /api/v1.0/tobs</h3>"
        f"<p>Usage Example: <em>localhost:5000/api/v1.0/(start date) [YYYY-mm-dd]</em><p>"
        f"<h3>4. /api/v1.0/(start day [YYYY-mm-dd])</h3>"
        f"<p>Usage Example: <em>localhost:5000/api/v1.0/(start)/(end) [YYYY-mm-dd]</em><p>"
        f"<h3>5. /api/v1.0/(start)/(end)</h3>"
        f"<hr>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return daily wise precipitation"""
    # Query all Measuremets
    try:
        results = session.query(Measurement.date,Measurement.prcp).all()

        # Create a dictionary from the row data and append 
        # to a list of daily precipitation
        daily_prcp = {}
        for date,precipitation in results:
                daily_prcp[date] = precipitation
    
        return (
                jsonify(daily_prcp)
             )
    except Exception as e:
        print(f"Error ocurred {e} Please Retry!")
        return redirect(url_for('welcome'))

@app.route("/api/v1.0/stations")
def station():
    """Return list of stations"""
    # Query all station names
    results = session.query(Station.station).all()

    # Create a dictionary of all stations 
    station_list = list(np.ravel(results))
  
    return (
        jsonify(station_list)
    )


@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature list for an year from last date of measurement"""
    last_measurement_date = dt.datetime.strptime(session.query(func.max(Measurement.date))\
                                             .first()[0], '%Y-%m-%d').date()
    last_12_months = last_measurement_date - dt.timedelta(days = 365)
    # Query all Measuremets
    results = session.query(Measurement.date, Measurement.tobs)\
                        .filter(Measurement.date >= last_12_months)\
                        .all()

    # Create a dictionary from the row data and append 
    # to a list of daily precipitation
    tobs_for_date = {}
    for date,tobs in results:
        tobs_for_last_year[date] = tobs
    
    return (
        jsonify(tobs_for_last_year)
    )

@app.route("/api/v1.0/<start>")
def temp_stats(start):
    """Return Min temp, Avg Temp and Max Temp for a start date"""
    start = dt.datetime.strptime(start,"%Y-%m-%d").date()
    
    # Query all Measuremets
    stmt = [func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)]
    results = session.query(*stmt)\
                        .filter(Measurement.date == start)\
                        .all()
    
    # to a list of Min, Avg and Max Temp
    tobs_stats_date = {}
    minT, avgT,maxT = zip(*results)
    tobs_stats_date["Min Temperature"] = minT
    tobs_stats_date["Avg Temperature"] = avgT
    tobs_stats_date["Max Temperature"] = maxT
    #list(np.ravel(results))

    return (
        jsonify(tobs_stats_date)
    )

@app.route("/api/v1.0/<start>/<end>")
def temp_stats_bet_dates(start, end):
    """Return Min temp, Avg Temp and Max Temp between start date and end date"""
    start = dt.datetime.strptime(start,"%Y-%m-%d").date()
    end = dt.datetime.strptime(end,"%Y-%m-%d").date()
    
    # Query all Measuremets
    stmt = [func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)]
    results = session.query(*stmt)\
                        .filter(and_(Measurement.date >= start, Measurement.date <= end))\
                        .all()
    
    # to a list of Min, Avg and Max Temp
    tobs_stats_bet_dates = {}
    minT, avgT,maxT = zip(*results)
    tobs_stats_bet_dates["Min Temperature"] = minT
    tobs_stats_bet_dates["Avg Temperature"] = avgT
    tobs_stats_bet_dates["Max Temperature"] = maxT
    #list(np.ravel(results))

    return (
        jsonify(tobs_stats_bet_dates)
    )


if __name__ == '__main__':
    app.run(debug=True)

