import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert "/static/index.html" in response.headers.get("location", "")

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_success():
    email = "testuser@example.com"
    activity = "Chess Club"
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()
    # Check participant added
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]

def test_signup_duplicate():
    email = "dupe@example.com"
    activity = "Programming Class"
    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")
    # Duplicate signup
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json().get("detail", "")

def test_signup_invalid_activity():
    email = "nobody@example.com"
    activity = "Nonexistent Club"
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 404
    assert "not found" in response.json().get("detail", "")

def test_signup_at_capacity():
    activity = "Gym Class"
    # Import activities dict directly for test manipulation
    from src.app import activities
    activities[activity]["max_participants"] = 1
    email1 = "first@example.com"
    email2 = "second@example.com"
    # First signup
    client.post(f"/activities/{activity}/signup?email={email1}")
    # Second signup should fail
    response = client.post(f"/activities/{activity}/signup?email={email2}")
    assert response.status_code == 400
    assert "full" in response.json().get("detail", "")
