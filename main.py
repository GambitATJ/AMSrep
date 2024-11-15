from flask import Flask, render_template, request,redirect # Added missing import
from flask_sqlalchemy import SQLAlchemy
import json
from flask import session
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime  # Added missing import
import pymysql  # Add this line


# Add this line to register PyMySQL as the MySQL driver
pymysql.install_as_MySQLdb()

with open('config.json', 'r') as c:
    params = json.load(c)["params"]


local_server = True

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Modify the URI to explicitly specify PyMySQL
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/ams"
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db.init_app(app)


class Users(db.Model):
    username= db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone_num = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(50), nullable=False)

class Booking(db.Model):
    sno= db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(50), db.ForeignKey('users.username'))
    start= db.Column(db.String(50), nullable=False)
    end= db.Column(db.String(50), nullable=False)
    date= db.Column(db.Date, nullable=False)

class Aircraft(db.Model):
    AircraftID= db.Column(db.Integer, primary_key=True)
    Name= db.Column(db.String(100), nullable=False)
    Airline = db.Column(db.String(50), nullable=False)
    Code = db.Column(db.String(20), nullable=False)

class Airline(db.Model):
    AirlineID= db.Column(db.Integer, primary_key=True)
    Name= db.Column(db.String(100), nullable=False)
    Code = db.Column(db.String(10), nullable=False)

class Airport(db.Model):
    AirportID= db.Column(db.String(5), primary_key=True)
    Name= db.Column(db.String(100), nullable=False)
    City= db.Column(db.String(100), nullable=False)
    Address= db.Column(db.String(100), nullable=False)
    Code = db.Column(db.String(6), nullable=False)

class Flight(db.Model):
    FlightNo= db.Column(db.String(20), primary_key=True)
    Airline_Name= db.Column(db.String(20), nullable=False)
    AircraftID= db.Column(db.Integer, db.ForeignKey('aircraft.AircraftID'))
    Origin = db.Column(db.String(50), db.ForeignKey('airport.AirportID'))
    Destination= db.Column(db.String(50), db.ForeignKey('airport.AirportID'))
    Duration= db.Column(db.Integer, nullable=False)
    
class Schedule(db.Model):
    ScheduleID= db.Column(db.Integer, primary_key=True)
    FlightNo= db.Column(db.String(20), db.ForeignKey('flight.FlightNo'))
    DayOfWeek= db.Column(db.String(20), nullable=False)
    DepartureTime= db.Column(db.Time, nullable=False)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/admin")
def admin():
    return render_template('admin.html')

@app.route("/airline")
def airline():
    return render_template('airline.html')

@app.route("/helpdesk")
def helpdesk():
    return render_template('helpdesk.html')

@app.route("/searchuser", methods=['GET', 'POST'])
def searchuser():
    users = Users.query.filter(Users.username==request.form.get('searchh'))
            
    return render_template('searchuser.html', users= users)
    
@app.route("/searchairline", methods=['GET', 'POST'])
def searchairline():
    airline = Airline.query.filter(Airline.AirlineID==request.form.get('airline'))
    return render_template('searchairline.html', airline= airline)

@app.route("/addsch", methods=['GET', 'POST'])
def addsch():
    if request.method == 'POST':
        ScheduleID = request.form.get('a1')
        FlightNo = request.form.get('a2')
        DayOfWeek = request.form.get('a3')
        DepartureTime = request.form.get('a4')
        entry = Schedule(ScheduleID=ScheduleID, FlightNo=FlightNo, DayOfWeek=DayOfWeek, DepartureTime=DepartureTime)
        db.session.add(entry)
        db.session.commit()
    
    # Fetch all FlightNo values to display in the dropdown
    flight_numbers = Flight.query.with_entities(Flight.FlightNo).all()
    return render_template('addsch.html', flight_numbers=flight_numbers)


@app.route("/addacc", methods = ['GET', 'POST'])
def addacc():
    if(request.method=='POST'):
        username = request.form.get('username')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        entry = Users(username=username, name=name, phone_num = phone, email = email )
        db.session.add(entry)
        db.session.commit()
    return render_template('addacc.html')

@app.route("/addairport", methods = ['GET', 'POST'])
def addairport():
    if(request.method=='POST'):
        AirportID = request.form.get('airportid')
        Name = request.form.get('name')
        City = request.form.get('city')
        Address = request.form.get('address')
        Code = request.form.get('code')
        entry = Airport(AirportID=AirportID, Name=Name, City = City, Address = Address, Code= Code )
        db.session.add(entry)
        db.session.commit()
    return render_template('addairport.html')

@app.route("/addairline", methods = ['GET', 'POST'])
def addairline():
    if(request.method=='POST'):
        AirlineID = request.form.get('airlineid')
        Name = request.form.get('name')
        Code = request.form.get('code')
        entry = Airline(AirlineID=AirlineID, Name=Name, Code= Code )
        db.session.add(entry)
        db.session.commit()
    return render_template('addairline.html')

@app.route("/addaircraft", methods = ['GET', 'POST'])
def addaircraft():
    if(request.method=='POST'):
        AircraftID = request.form.get('aircraftid')
        Name = request.form.get('name')
        Airlines = request.form.get('airline')
        Code = request.form.get('code')
        entry = Aircraft(AircraftID=AircraftID, Name=Name, Airline=Airlines, Code= Code )
        db.session.add(entry)
        db.session.commit()

    airline_names = Airline.query.with_entities(Airline.Name).all()
    return render_template('addaircraft.html', airline_names=airline_names)

@app.route("/addflight", methods = ['GET', 'POST'])
def addflight():
    if(request.method=='POST'):
        FlightNo = request.form.get('FlightNo')
        Airline_Name = request.form.get('airlinename')
        AircraftID = request.form.get('aircraftid')
        Origin = request.form.get('origin')
        Destination = request.form.get('destination')
        Duration = request.form.get('duration')
        entry = Flight(FlightNo=FlightNo, Airline_Name=Airline_Name, AircraftID=AircraftID, Origin=Origin, Destination=Destination, Duration= Duration)
        db.session.add(entry)
        db.session.commit()

    
    airline_names= Airline.query.with_entities(Airline.Name).all()
    aircraft_id = Aircraft.query.with_entities(Aircraft.AircraftID).all()
    origins = Airport.query.with_entities(Airport.City).all()
    destinations = Airport.query.with_entities(Airport.City).all()
    return render_template('addflight.html', airline_names=airline_names, aircraft_id=aircraft_id, origins=origins, destinations=destinations)



@app.route("/dltsch", methods = ['GET', 'POST'])
def dltsch():
    schedule = Schedule.query.filter(Schedule.ScheduleID==request.form.get('schedule')) 
    return render_template('dltsch.html', schedule=schedule)

@app.route("/srchsch", methods = ['GET', 'POST'])
def srchsch():
    results = db.session.query(Flight, Schedule, Aircraft)\
        .join(Schedule, Flight.FlightNo == Schedule.FlightNo)\
        .join(Aircraft, Flight.AircraftID == Aircraft.AircraftID)\
        .filter(Flight.Origin==request.form.get('origin'), Flight.Destination==request.form.get('destination'))\
        .all()
            
    return render_template('srchsch.html', combined_data=results)

@app.route("/cancel/<int:sno>" , methods=['GET', 'POST'])
def cancel(sno):
    booking = Booking.query.filter_by(sno=sno).first()
    db.session.delete(booking)
    db.session.commit()
    return redirect("/cancelticket")

@app.route("/cancelsch/<int:ScheduleID>" , methods=['GET', 'POST'])
def cancelsch(ScheduleID):
    schedule = Schedule.query.filter_by(ScheduleID=ScheduleID).first()
    db.session.delete(schedule)
    db.session.commit()
    return redirect("/dltsch")

@app.route("/delete/<int:sno>" , methods=['GET', 'POST'])
def delete(sno):
    contacts = Contacts.query.filter_by(sno=sno).first()
    db.session.delete(contacts)
    db.session.commit()
    return redirect("/srchsch")

@app.route("/srchfli", methods=['GET', 'POST'])
def srchfli():
    flight = Flight.query.filter(Flight.Origin==request.form.get('origin'), Flight.Destination==request.form.get('destination'))
    return render_template('srchfli.html', flight= flight)

@app.route("/cancelticket", methods=['GET', 'POST'])
def cancelticket():
    booking = Booking.query.filter(Booking.username==request.form.get('cancel'))
            
    return render_template('cancelticket.html', booking= booking)

@app.route("/bookticket", methods = ['GET', 'POST'])
def bookticket():
    if(request.method=='POST'):
        username1 = request.form.get('uname')
        start1 = request.form.get('start')
        end1 = request.form.get('end')
        date1 = request.form.get('date')
        entry = Booking(username=username1, start=start1, end = end1, date = date1 )
        db.session.add(entry)
        db.session.commit()
    userns= Users.query.with_entities(Users.username).all()
    startap= Airport.query.with_entities(Airport.City).all()
    return render_template('bookticket.html', userns=userns, startap=startap)



@app.route("/customer")
def customer():
    return render_template('customer.html')



app.run(debug=True)

