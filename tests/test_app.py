import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

# Test GET /activities

def test_get_activities():
    # Arrange
    # (TestClient already arranged)
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0

# Test POST /activities/{activity}/signup

def test_signup_activity():
    # Arrange
    response = client.get("/activities")
    activities = list(response.json().keys())
    activity = activities[0]
    email = "testuser@mergington.edu"
    
    # Act
    signup_resp = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert signup_resp.status_code == 200
    result = signup_resp.json()
    assert "message" in result

# Test POST /activities/{activity}/unregister

def test_unregister_activity():
    # Arrange
    response = client.get("/activities")
    activities = list(response.json().keys())
    activity = activities[0]
    email = "testuser@mergington.edu"
    client.post(f"/activities/{activity}/signup?email={email}")  # Ensure user is signed up
    
    # Act
    unregister_resp = client.post(f"/activities/{activity}/unregister?email={email}")
    
    # Assert
    assert unregister_resp.status_code == 200
    result = unregister_resp.json()
    assert "message" in result

# Edge case: signup for full activity

def test_signup_full_activity():
    # Arrange
    response = client.get("/activities")
    activities = response.json()
    for name, details in activities.items():
        if details["max_participants"] == 1:
            activity = name
            break
    else:
        activity = list(activities.keys())[0]
        # artificially fill up
        client.post(f"/activities/{activity}/signup?email=full1@mergington.edu")
        client.post(f"/activities/{activity}/signup?email=full2@mergington.edu")
    email = "overflow@mergington.edu"
    
    # Act
    signup_resp = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert signup_resp.status_code in (400, 409)
    result = signup_resp.json()
    assert "detail" in result

# Edge case: unregister non-existent participant

def test_unregister_nonexistent():
    # Arrange
    response = client.get("/activities")
    activity = list(response.json().keys())[0]
    email = "notfound@mergington.edu"
    
    # Act
    unregister_resp = client.post(f"/activities/{activity}/unregister?email={email}")
    
    # Assert
    assert unregister_resp.status_code in (400, 404)
    result = unregister_resp.json()
    assert "detail" in result
