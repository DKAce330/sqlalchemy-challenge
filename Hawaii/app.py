# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base=automap_base()

# reflect the tables
Base.prepare(engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session=Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#With help from bard
# Define a function which calculates and returns the the date one year from the most recent date
def query_date():
    most_recent_date = session.query(func.max(Measurement.date)).first()[0]
    query_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)


#################################################
# Flask Routes
#################################################
#Homepage with descriptive routes
@app.route('/')
def landing():
    return """ <h1> Welcome to the home page of the hawaii rain api </h1>
    <h3> Available routes: </h3>
    <li><a href = "/api/v1.0/precipitation"> Precipitation</a>: <strong>/api/v1.0/precipitation</strong> </li>
    <li><a href = "/api/v1.0/stations"> Stations </a>: <strong>/api/v1.0/stations</strong></li>
    <li><a href = "/api/v1.0/tobs"> TOBS </a>: <strong>/api/v1.0/tobs</strong></li>
    <li>To retrieve the minimum, average, and maximum temperatures for a specific date, use <strong>/api/v1.0/&ltstart&gt</strong> (replace start with yyyy-mm-dd format)</li>
    <li>To retrieve minimum, average, and maximum temperatures for a start-end range, <strong>/api/v1.0/&ltstart&gt/&ltend&gt</strong> (replace both the start and end date in yyyy-mm-dd format)</li>
    </ul>
    """
#Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    #Query data
    data = session.query(Measurement.prcp, Measurement.date).all()
    session.close()
    #Create a dictionary and append row data to return as a json
    prcp_list = []
    for date, prcp in data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)
    return jsonify(prcp_list)
    
#Station route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Query data, convert, return as json
    station_data= session.query(Station.station,Station.id).all()
    session.close()
    station_list = list(np.ravel(station_data))
    return jsonify(station_list)

#Tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Query data, convert, return as json
    tobs_data = session.query(Measurement.tobs).all()  # Fetch all results
    session.close()

    tobs_list = []
    for row in tobs_data:
        tobs_value = row[0]  # Extract the first column value (tobs)
        tobs_dict = {"tobs": tobs_value}  # Create a dictionary with the tob value
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


#Start/Start-End route
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    # Create query
    start_date_tobs_results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()
    # Create list to be returned as json
    start_date_tobs_values =[]
    for min, avg, max in start_date_tobs_results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min"] = min
        start_date_tobs_dict["average"] = avg
        start_date_tobs_dict["max"] = max
        start_date_tobs_values.append(start_date_tobs_dict)
    
    return jsonify(start_date_tobs_values)

@app.route("/api/v1.0/<start>/<end>")
def Start_end_date(start, end):
    session = Session(engine)
    #create query
    start_end_date_tobs_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()
    #create list to return as json
    start_end_tobs_date_values = []
    for min, avg, max in start_end_date_tobs_results:
        start_end_tobs_date_dict = {}
        start_end_tobs_date_dict["min_temp"] = min
        start_end_tobs_date_dict["avg_temp"] = avg
        start_end_tobs_date_dict["max_temp"] = max
        start_end_tobs_date_values.append(start_end_tobs_date_dict) 

    return jsonify(start_end_tobs_date_values)
    
#Main branch 
if __name__ == "__main__":
    app.run(debug = True)