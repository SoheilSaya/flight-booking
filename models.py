from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, Enum
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String)
    phone_number = Column(String)

class Passenger(Base):
    __tablename__ = "Passenger"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    name = Column(String)
    national_id = Column(String)
    age = Column(Integer)
    gender = Column(Enum("Male", "Female"))

class Order(Base):
    __tablename__ = "Order"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    code = Column(String)
    price = Column(DECIMAL(10, 2))

class Ticket(Base):
    __tablename__ = "Ticket"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("Order.id"), nullable=False)
    ticket_number = Column(String)

class Airport(Base):
    __tablename__ = "Airport"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    code = Column(String, unique=True)
