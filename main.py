from fastapi import FastAPI, Form, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Date, Integer, ForeignKey
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import random

# Setup
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
templates = Jinja2Templates(directory="templates")
bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
DATABASE_URL = "mysql+aiomysql://root:@localhost/flight_booking"
async_engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)
Base = declarative_base()

# Models
# User Model
class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    phone_number = Column(String)

# Airport Model
class Airport(Base):
    __tablename__ = "airport"
    code = Column(String, primary_key=True, unique=True, index=True)
    name = Column(String)

    # No relationships here since airports are referenced in flights.

# Flight Model
class Flight(Base):
    __tablename__ = "flight"
    id = Column(Integer, primary_key=True, index=True)
    departure_code = Column(String, ForeignKey("airport.code"))
    destination_code = Column(String, ForeignKey("airport.code"))
    flight_date = Column(Date)

    # Relationships for accessing departure and destination airports
    departure_airport = relationship("Airport", foreign_keys=[departure_code])
    destination_airport = relationship("Airport", foreign_keys=[destination_code])

    # Relationship for tickets associated with this flight
    tickets = relationship("Ticket", back_populates="flight")

# Passenger Model
class Passenger(Base):
    __tablename__ = "passenger"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    national_id = Column(String, unique=True, index=True)
    age = Column(Integer)
    gender = Column(String)

    # Relationship for tickets associated with this passenger
    tickets = relationship("Ticket", back_populates="passenger")

# Order Model
class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True)
    price = Column(Integer)

    # Relationship for tickets in this order
    tickets = relationship("Ticket", back_populates="order")

# Ticket Model
class Ticket(Base):
    __tablename__ = "ticket"
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, unique=True)
    passenger_id = Column(Integer, ForeignKey("passenger.id"))
    flight_id = Column(Integer, ForeignKey("flight.id"))
    order_id = Column(Integer, ForeignKey("order.id"))

    # Relationships to access related models
    passenger = relationship("Passenger", back_populates="tickets")
    flight = relationship("Flight", back_populates="tickets")
    order = relationship("Order", back_populates="tickets")

# Initialize database
@app.on_event("startup")
async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Dependency to get async DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Helper functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_token_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token.split(" ")[1]

# Routes
@app.get("/", response_class=HTMLResponse)
async def show_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user or not bcrypt.verify(password, user.password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    access_token = create_access_token(data={"sub": username})
    response = RedirectResponse(url="/menu", status_code=302)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/signup", response_class=HTMLResponse)
async def show_signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup", response_class=HTMLResponse)
async def signup(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    phone_number: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.username == username))
    if result.scalars().first():
        return templates.TemplateResponse("signup.html", {"request": request, "error": "User already exists"})
    
    hashed_password = bcrypt.hash(password)
    new_user = User(username=username, password=hashed_password, name=name, phone_number=phone_number)
    db.add(new_user)
    await db.commit()
    return RedirectResponse("/", status_code=302)

@app.get("/menu", response_class=HTMLResponse)
async def show_menu(request: Request, db: AsyncSession = Depends(get_db), token: str = Depends(get_token_from_cookie)):
    result = await db.execute(select(Airport))
    airports = result.scalars().all()
    return templates.TemplateResponse("menu.html", {"request": request, "airports": airports})

@app.post("/search_flights", response_class=HTMLResponse)
async def search_flights(
    request: Request,
    departure: str = Form(...),
    destination: str = Form(...),
    flight_date: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Flight).where(
        Flight.departure_code == departure,
        Flight.destination_code == destination,
        Flight.flight_date == flight_date
    ))
    flights = result.scalars().all()
    return templates.TemplateResponse("menu.html", {"request": request, "flights": flights})

@app.get("/buy_ticket/{flight_id}", response_class=HTMLResponse)
async def buy_ticket(flight_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Flight).where(Flight.id == flight_id))
    flight = result.scalars().first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    result = await db.execute(select(Passenger))
    passengers = result.scalars().all()
    return templates.TemplateResponse(
        "buy_ticket.html",
        {"request": request, "flight": flight, "passengers": passengers},
    )

@app.post("/add_passenger", response_class=HTMLResponse)
async def add_passenger(
    request: Request,
    name: str = Form(...),
    national_id: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    new_passenger = Passenger(name=name, national_id=national_id, age=age, gender=gender)
    db.add(new_passenger)
    await db.commit()
    return RedirectResponse(url="/menu", status_code=302)

@app.post("/checkout_page", response_class=HTMLResponse)
async def checkout_page(
    request: Request,
    passenger_ids: list[int] = Form(...),
    flight_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
):
    if not passenger_ids:
        raise HTTPException(status_code=400, detail="No passengers selected")

    price_per_ticket = 500
    total_price = price_per_ticket * len(passenger_ids)

    order_code = f"ORDER-{random.randint(1000, 9999)}"

    try:
        new_order = Order(code=order_code, price=total_price)
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)

        for passenger_id in passenger_ids:
            ticket_number = f"TICKET-{random.randint(10000, 99999)}"
            new_ticket = Ticket(
                ticket_number=ticket_number,
                passenger_id=passenger_id,
                flight_id=flight_id,
                order_id=new_order.id,
            )
            db.add(new_ticket)

        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    return templates.TemplateResponse(
        "checkout.html",
        {"request": request, "order_code": order_code, "total_price": total_price},
    )
