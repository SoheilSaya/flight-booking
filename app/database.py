from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+aiomysql://root:@localhost/flight_booking"

async_engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
