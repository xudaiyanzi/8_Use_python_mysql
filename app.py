import numpy as np

import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
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
        f"Available Routes:<br/>"
        f"<br/>"
        f"1. returns all the precipitation data: <br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"<br/>"
        f"2. returns all the station data: <br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"<br/>"
        f"3. returns a JSON list of Temperature Observations (tobs) for the previous year<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"<br/>"
        f"4. returns a JSON list of the minimum temperature, the average temperature, and the max temperature from a given start date<br/>"
        f"<br/>"
        f"/api/v1.0/<start_date>(input a start_date:YYYY-MM-DD)<br/>"
        f"<br/>"
        f"<br/>"
        f"5. returns a JSON list of the minimum temperature, the average temperature, and the max temperature within a given start date and end date<br/>"
        f"<br/>"
        f"/api/v1.0/<start>(input a start_date:YYYY-MM-DD)/<end>(input a end_date:YYYY-MM-DD)<br/>"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query all passengers
    results = session.query(Measurement).all()

    # Create a dictionary from the row data and append to a list of all_passengers
    precipitation_all = [] 
    
    for result in results:
        
        precipitation_dict = {}      
        precipitation_dict["date"] = result.date
        precipitation_dict["precipitation"] = result.prcp
        precipitation_all.append(precipitation_dict)
        
    return jsonify(precipitation_all)



@app.route("/api/v1.0/stations")
def stations():
    # Query all passengers
    results = session.query(Station).all()
    
    # Create a dictionary from the row data and append to a list of all_passengers
    station_name = []
    
    for result in results:
        station_dict = {}
        station_dict["station"] = result.station
        station_name.append(station_dict)
    
    return jsonify(station_name)



@app.route("/api/v1.0/tobs")
def tobs():
    # 1) find the lastest date, -- so we could the exact months of the last 12 months
    last_date_result = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #### store the last date
    last_date = last_date_result[0]
    #### conver the string of date into date format
    last_date_format = dt.datetime.strptime(last_date , '%Y-%m-%d')
    
    # 2) Calculate the date 1 year ago from the last data point in the database
    #### import relativedelta to find the date of 12 month before the last_date
    from dateutil.relativedelta import relativedelta
    Date_12months = last_date_format + relativedelta(months=-12)
    
    # 3) filter and store the data within 12 month and group by date
    Last_12Month=session.query(Measurement.date,func.sum(Measurement.prcp).\
                                         label("precipitation")).group_by(Measurement.date).\
                                         filter(Measurement.date >=Date_12months).all()
    
    tobs_all = []
                                 
    for row in Last_12Month:
        tobs_dict = {}
        tobs_dict["date"] = row.date
        tobs_dict["precipitation"] = row.precipitation
        tobs_all.append(tobs_dict)
    
    #date_prcp_sum_new.head()
    #tobs_all
    return jsonify(tobs_all)
        

@app.route("/api/v1.0/<start_date>")
def start(start_date):
    
    T_info = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                                  filter(Measurement.date >= start_date).all()
    
    return jsonify(T_info)




@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date,end_date):
    
    T_info2 = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                                  filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    return jsonify(T_info2)
        
        
if __name__ == '__main__':
    app.run()



