from fastapi import FastAPI
from app.models import Base
from app.database import async_engine
from app.routes import auth, flights, passengers

app = FastAPI()

@app.on_event("startup")
async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(flights.router, prefix="/flights", tags=["Flights"])
app.include_router(passengers.router, prefix="/passengers", tags=["Passengers"])
