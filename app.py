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

    return(f"Welcome to the Hawaii Climate API!<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/stations ~~~~~ a list of all weather observation stations<br/>"
            f"/api/v1.0/precipitaton ~~ the latest year of preceipitation data<br/>"
            f"/api/v1.0/tobs ~~ list of the latest year of temperature data<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
            f"~~~ datesearch format: (yyyy-mm-dd)<br/>"
            f"/api/v1.0/2015-05-30  ~~~~~~~~~~~ low, high, and average temp for date given and each date after<br/>"
            f"/api/v1.0/2015-05-30/2016-01-30 ~~ low, high, and average temp for date given and each date up to and including end date<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
            f"~ data available from 2010-01-01 to 2017-08-23 ~<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
#next route
@app.route("/api/v1.0/precipitation")
def precipitation():

    #create session link from python to db
    session = Session(engine)

     #set up query that will pull date column and put in desc order and then will pick first value to get latest date
    latest_date_query = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    #make into a list that we can grab from
    latest_date_list= list(np.ravel(latest_date_query))[0]

    #latest_date_list returned 8-23-2017 - knowing that we can create last_year variable
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #query all measurements
    prcp_results = session.query(Measurement.date, Measurement.prcp, Measurement.station).\
        filter(Measurement.date >= last_year).all()

    #close session
    session.close()

    #make a list to store dict
    precipitation = []

    #for loop to create dict and append to precipitation list above
    for result in prcp_results:
        prcp_dict = {"Date": "Precipitation"}
        prcp_dict["Date"]= result[0]
        prcp_dict["Precipitation"] = result[1]
        prcp_dict["Station"] = result[2]
        precipitation.append(prcp_dict)
    
    #return json
    return jsonify(precipitation)

#next route
@app.route("/api/v1.0/stations")
def stations():
    #create session link from python to db
    session = Session(engine)

    #create query
    station_results = session.query(Station.station).all()

    #list of stations - Convert list of tuples into normal list
    station_list = list(np.ravel(station_results))
  
    #return json
    return jsonify(station_list)

#next route
#when are we calling the most active station?
@app.route("/api/v1.0/tobs")
def temperature():
    #create session link from python to db
    session = Session(engine)

    #set up query that will pull date column and put in desc order and then will pick first value to get latest date
    latest_date_query = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    #make into a list that we can grab from
    latest_date_list= list(np.ravel(latest_date_query))[0]

    #latest_date_list returned 8-23-2017 - knowing that we can create last_year variable
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #most active station
    #active_station = session.query(Station.station, func.count(Station.station)).\
        #group_by(Measurement.station).\
        #order_by(func.count(Measurement.station).desc()).all()
    

    #take out data within last year - may not need .filter(Measurement.station == "USC00519281" ) - if I do, how to do I use above to call it?
    last_year_temps = session.query(Measurement.tobs).filter(Measurement.date >= last_year).filter(Measurement.station == "USC00519281" ).all()

    #close query
    session.close()

    #convert tuple to a list
    temp_list = list(np.ravel(last_year_temps))


    #jsonify
    return jsonify(temp_list)

#next route
#how can I get it pull out the date the user types in (activity 10 of hw?)
@app.route("/api/v1.0/<start>")
def single_date(start):

    
    #sel min, max, avg based on a date
    sel = [Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.round(func.avg(Measurement.tobs))]

    #set up query for the above and use strftime to allow input of date and all dates after
    results = session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date)>= start).group_by(Measurement.date).all()

    #close session
    session.close()

    #similar to above, set up empty list and create dict to go in it
    date_temp_stats = []

    #for loop
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Min Temp"] = result[1]
        date_dict["Max Temp"] = result[2]
        date_dict["Avg Temp"] = result[3]
        date_temp_stats.append(date_dict)

    #close session
    #session.close()

    #make into list
    #date_stats_list = list(np.ravel(date_stats))

    #jsonify
    return jsonify(date_temp_stats)

@app.route('/api/v1.0/<startDate>/<endDate>')
def startEnd(startDate, endDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate)
                       .group_by(Measurement.date)
                       .all())
    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)

    return jsonify(dates)


if __name__ == "__main__":
	app.run(debug=True)
