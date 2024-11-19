# conftest.py
import pytest
from fastapi.testclient import TestClient
from main import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base

# Setup an in-memory SQLite database for testing
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the `get_db` dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply database setup
Base.metadata.create_all(bind=engine)
app.dependency_overrides[get_db] = override_get_db

# Create a TestClient
client = TestClient(app)

@pytest.fixture
def test_client():
    yield client
