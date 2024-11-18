from fastapi import FastAPI, Form, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, String, Date, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.hash import bcrypt
import time
import random

# FastAPI app setup
app = FastAPI()

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
DATABASE_URL = "mysql+mysqlconnector://root:@localhost/flight_booking"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
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

class Passenger(Base):
    __tablename__ = "passenger"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    national_id = Column(String, unique=True, index=True)
    age = Column(Integer)
    gender = Column(String)

class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True)
    price = Column(Integer)

class Ticket(Base):
    __tablename__ = "ticket"
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, unique=True)
    passenger_id = Column(Integer, ForeignKey("passenger.id"))
    flight_id = Column(Integer, ForeignKey("flight.id"))
    order_id = Column(Integer, ForeignKey("order.id"))

Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/", response_class=HTMLResponse)
def show_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if user and bcrypt.verify(password, user.password):
        return RedirectResponse("/menu", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/signup", response_class=HTMLResponse)
def show_signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup", response_class=HTMLResponse)
def signup(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    phone_number: str = Form(...),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse("signup.html", {"request": request, "error": "User already exists"})
    hashed_password = bcrypt.hash(password)
    new_user = User(username=username, password=hashed_password, name=name, phone_number=phone_number)
    db.add(new_user)
    db.commit()
    return RedirectResponse("/", status_code=302)

@app.get("/menu", response_class=HTMLResponse)
def show_menu(request: Request, db: Session = Depends(get_db)):
    airports = db.query(Airport).all()
    return templates.TemplateResponse("menu.html", {"request": request, "airports": airports, "flights": None})

@app.post("/search_flights", response_class=HTMLResponse)
def search_flights(
    request: Request,
    departure: str = Form(...),
    destination: str = Form(...),
    flight_date: str = Form(...),
    db: Session = Depends(get_db)
):
    flights = db.query(Flight).filter(
        Flight.departure_code == departure,
        Flight.destination_code == destination,
        Flight.flight_date == flight_date
    ).all()
    airports = db.query(Airport).all()
    return templates.TemplateResponse("menu.html", {"request": request, "airports": airports, "flights": flights})

@app.get("/buy_ticket/{flight_id}", response_class=HTMLResponse)

def buy_ticket(flight_id: int, request: Request, db: Session = Depends(get_db)):
    print("Flight ID received:", flight_id)
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    print("Flight found:", flight)

    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    passengers = db.query(Passenger).all()
    return templates.TemplateResponse(
        "buy_ticket.html",
        {"request": request, "flight": flight, "passengers": passengers},
    )
@app.post("/add_passenger", response_class=HTMLResponse)
def add_passenger(
    request: Request,
    name: str = Form(...),
    national_id: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    departure_code: str = Form(...),
    destination_code: str = Form(...),
    flight_date: str = Form(...),
    db: Session = Depends(get_db)
):
    # Add the new passenger to the database
    new_passenger = Passenger(name=name, national_id=national_id, age=age, gender=gender)
    db.add(new_passenger)
    db.commit()

    # Redirect back to the /buy_ticket page for the same flight
    return RedirectResponse(
        url=f"/buy_ticket/{request.path_params.get('flight_id', 1)}", status_code=302
    )

# Checkout route
@app.post("/checkout_page", response_class=HTMLResponse)
def checkout_page(
    request: Request,
    passenger_ids: list[int] = Form(...),
    flight_id: int = Form(...),
    db: Session = Depends(get_db)
):
    if not passenger_ids:
        raise HTTPException(status_code=400, detail="No passengers selected")

    # Calculate the total price
    price_per_ticket = 500
    total_price = price_per_ticket * len(passenger_ids)

    # Generate a unique order code
    order_code = f"ORDER-{random.randint(1000, 9999)}"

    try:
        # Save the order to the database
        new_order = Order(code=order_code, price=total_price)
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        # Create tickets for each passenger and save them
        for passenger_id in passenger_ids:
            ticket_number = f"TICKET-{random.randint(10000, 99999)}"
            new_ticket = Ticket(
                ticket_number=ticket_number,
                passenger_id=passenger_id,
                flight_id=flight_id,
                order_id=new_order.id
            )
            db.add(new_ticket)

        # Commit all tickets
        db.commit()

    except Exception as e:
        # Rollback in case of any error and raise an HTTPException
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    # Render the checkout success page
    return templates.TemplateResponse(
        "checkout.html",
        {"request": request, "order_code": order_code, "total_price": total_price}
    )

