#Dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

#Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#Reflect Database
Base = automap_base()
Base.prepare(engine, reflect = True)

#Save table references
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create session
session = Session(engine)

#Create Flask

app=Flask(__name__)

# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
#def calc_temps(start_date, end_date):
# """TMIN, TAVG, and TMAX for a list of dates.
    
#Args:
    #start_date (string): A date string in the format %Y-%m-%d
    #end_date (string): A date string in the format %Y-%m-%d
        
#Returns:
    #TMIN, TAVG, and TMAX
    #"""
    
    #return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        #filter(Measurement.date >= start_date).\
        #filter(Measurement.date <= end_date).all()

#first route
@app.route("/")
def main ():
    #list all routes available

    return(f"Available Routes : <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>")

#next route
@app.route("/api/v1.0/precipitation")
def precipitation():

    #print response
    print("Received precipitation API request")

    #query all measurements
    prcp_results = session.query(Measurement.date, Measurement.prcp).\
                   filter(Measurement.date.between('2016-08-01', '2017-08-01')).all()

    #make a list to store dict
    precipitation = []

    #for loop to create dict and append to precipitation list above
    for result in prcp_results:
        prcp_dict = {"Date": "Precipitation"}
        prcp_dict["Date"]= result[0]
        prcp_dict["Precipitation"] = result[1]
        precipitation.append(prcp_dict)
    
    #return json
    return jsonify(precipitation)

#next route
@app.route("/api/v1.0/stations")
def stations():

    #print response
    print("Received precipitation API request")

    #create query
    station_results = session.query(Station.station, Station.name).group_by(Station.station).all()

    #list of stations
    station_list = []
    
    #for loop to create json list of stations from dataset
    for station in station_list:
        station_dict = {"Station": "Name"}
        station_dict["Station"] =station[0]
        station_dict["Name"]=station[1]
        station_list.append(station_dict)
    
    #return json
    return jsonify(station_list)


if __name__ == "__main__":
	app.run(debug=True)
