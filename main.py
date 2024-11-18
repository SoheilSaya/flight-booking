from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, String, Date, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.hash import bcrypt

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
    return templates.TemplateResponse("menu.html", {"request": request, "airports": airports})

@app.post("/search_flights", response_class=HTMLResponse)
def search_flights(
    request: Request,
    departure: str = Form(...),
    destination: str = Form(...),
    flight_date: str = Form(...),
    db: Session = Depends(get_db),
):
    flights = db.query(Flight).filter(
        Flight.departure_code == departure,
        Flight.destination_code == destination,
        Flight.flight_date == flight_date,
    ).all()
    return templates.TemplateResponse(
        "menu.html",
        {
            "request": request,
            "flights": flights,
            "departure": departure,
            "destination": destination,
            "flight_date": flight_date,
            "airports": db.query(Airport).all(),
        },
    )
