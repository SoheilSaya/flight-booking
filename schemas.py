from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    phone_number: str


class Airport(BaseModel):
    name: str
    code: str

    class Config:
        orm_mode = True  # Allows using SQLAlchemy objects directly
