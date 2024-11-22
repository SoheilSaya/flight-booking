# test_main.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_signup_user():
    response = client.post(
        "/signup",
        data={
            "username": "testuser12",
            "password": "testpass",
            "name": "Test User",
            "phone_number": "1234567890"
        }
    )
    assert response.status_code == 200  # Expecting 200 OK if rendering a success message
    assert "User already exists" not in response.text  # Ensure it's a successful signup

def test_login_user():
    # First, sign up the user to ensure they exist
    client.post(
        "/signup",
        data={
            "username": "testuserlogin",
            "password": "testpass",
            "name": "Login User",
            "phone_number": "0987654321"
        }
    )

    # Then, try to log in with correct credentials
    response = client.post(
        "/login",
        data={"username": "testuserlogin", "password": "testpass"}
    )
    assert response.status_code == 200  # Expecting 200 OK for a rendered login success page
    assert "Invalid credentials" not in response.text  # Ensure login was successful
