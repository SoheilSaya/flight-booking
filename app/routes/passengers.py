from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Passenger
from app.database import get_db

router = APIRouter()

@router.post("/add", response_class=HTMLResponse)
async def add_passenger(
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
