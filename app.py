# app.py (combining multiple files to keep file count low)
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import uvicorn
import bcrypt

# Database Configuration
DATABASE_URL = "mysql+mysqlconnector://root:@localhost/flight_booking"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User Model
class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(255))
    name = Column(String(100))
    phone_number = Column(String(20))

# Pydantic Models for Validation
class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    phone_number: str

class UserLogin(BaseModel):
    username: str
    password: str

# FastAPI Application
app = FastAPI()

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)

# Signup Endpoint
@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    existing_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash password
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    # Create new user
    db_user = UserModel(
        username=user.username, 
        password=hashed_password.decode('utf-8'),
        name=user.name,
        phone_number=user.phone_number
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User created successfully"}

# Login Endpoint
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Find user by username
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    
    # Validate credentials
    if not db_user or not bcrypt.checkpw(user.password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "message": "Login successful", 
        "user_menu": [
            {"id": 1, "name": "Profile"},
            {"id": 2, "name": "Book Flight"},
            {"id": 3, "name": "My Bookings"}
        ]
    }

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# requirements.txt content:
# fastapi
# uvicorn
# sqlalchemy
# mysql-connector-python
# bcrypt
# pydantic