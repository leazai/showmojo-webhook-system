'''
Tests for the ShowMojo webhook endpoint
'''

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database import Base, get_db

# Use a separate test database
TEST_DATABASE_URL = "sqlite:///./test.db"
os.environ['DATABASE_URL'] = TEST_DATABASE_URL

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def setup_database():
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the tables after the test
    Base.metadata.drop_all(bind=engine)


def test_receive_webhook_success(setup_database):
    '''Test successful webhook processing'''
    # Mock ShowMojo bearer token
    os.environ["SHOWMOJO_BEARER_TOKEN"] = "27ac6aadb42bb1fa05ef6167c5572674"

    headers = {"Authorization": "Bearer 27ac6aadb42bb1fa05ef6167c5572674"}
    payload = {
        "event": {
            "id": "evt-123",
            "action": "lead_created",
            "actor": "prospect",
            "created_at": "2025-10-31T10:00:00Z",
            "showing": {
                "uid": "shw-456",
                "name": "Test Prospect",
                "email": "test@example.com",
                "listing_uid": "lst-789",
                "listing_full_address": "123 Test St"
            }
        }
    }

    response = client.post("/webhook", headers=headers, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["event_id"] == "evt-123"

def test_receive_webhook_duplicate(setup_database):
    '''Test duplicate webhook processing'''
    os.environ["SHOWMOJO_BEARER_TOKEN"] = "27ac6aadb42bb1fa05ef6167c5572674"
    headers = {"Authorization": "Bearer 27ac6aadb42bb1fa05ef6167c5572674"}
    payload = {
        "event": {
            "id": "evt-123",
            "action": "lead_created",
            "actor": "prospect",
            "created_at": "2025-10-31T10:00:00Z",
            "showing": {
                "uid": "shw-456",
                "name": "Test Prospect",
                "email": "test@example.com",
                "listing_uid": "lst-789",
                "listing_full_address": "123 Test St"
            }
        }
    }

    # Send the webhook twice
    client.post("/webhook", headers=headers, json=payload)
    response = client.post("/webhook", headers=headers, json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "duplicate"

def test_receive_webhook_unauthorized(setup_database):
    '''Test webhook processing with invalid token'''
    os.environ["SHOWMOJO_BEARER_TOKEN"] = "27ac6aadb42bb1fa05ef6167c5572674"
    headers = {"Authorization": "Bearer wrong_token"}
    payload = {}

    response = client.post("/webhook", headers=headers, json=payload)
    assert response.status_code == 401
