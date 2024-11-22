from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Flight, Airport
from app.database import get_db

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def list_airports(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Airport))
    airports = result.scalars().all()
    return {"request": request, "airports": airports}

@router.post("/search", response_class=HTMLResponse)
async def search_flights(
    departure: str = Form(...),
    destination: str = Form(...),
    flight_date: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Flight).where(
        Flight.departure_code == departure,
        Flight.destination_code == destination,
        Flight.flight_date == flight_date,
    ))
    flights = result.scalars().all()
    return {"flights": flights}
