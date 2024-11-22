from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Date, Integer, ForeignKey

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    phone_number = Column(String)

class Airport(Base):
    __tablename__ = "airport"
    code = Column(String, primary_key=True, unique=True, index=True)
    name = Column(String)

class Flight(Base):
    __tablename__ = "flight"
    id = Column(Integer, primary_key=True, index=True)
    departure_code = Column(String, ForeignKey("airport.code"))
    destination_code = Column(String, ForeignKey("airport.code"))
    flight_date = Column(Date)

    departure_airport = relationship("Airport", foreign_keys=[departure_code])
    destination_airport = relationship("Airport", foreign_keys=[destination_code])
    tickets = relationship("Ticket", back_populates="flight")

class Passenger(Base):
    __tablename__ = "passenger"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    national_id = Column(String, unique=True, index=True)
    age = Column(Integer)
    gender = Column(String)
    tickets = relationship("Ticket", back_populates="passenger")

class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True)
    price = Column(Integer)
    tickets = relationship("Ticket", back_populates="order")

class Ticket(Base):
    __tablename__ = "ticket"
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, unique=True)
    passenger_id = Column(Integer, ForeignKey("passenger.id"))
    flight_id = Column(Integer, ForeignKey("flight.id"))
    order_id = Column(Integer, ForeignKey("order.id"))

    passenger = relationship("Passenger", back_populates="tickets")
    flight = relationship("Flight", back_populates="tickets")
    order = relationship("Order", back_populates="tickets")
