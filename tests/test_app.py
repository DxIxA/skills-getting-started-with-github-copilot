import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)

@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original_activities


def test_get_activities_returns_activity_list():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")
    result = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(result, dict)
    assert expected_activity in result
    assert result[expected_activity]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Programming Class"
    email = "teststudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )
    result = response.json()

    # Assert
    assert response.status_code == 200
    assert result["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_remove_participant_deletes_student():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    assert email in app_module.activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )
    result = response.json()

    # Assert
    assert response.status_code == 200
    assert result["message"] == f"Removed {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_signup_for_invalid_activity_returns_404():
    # Arrange
    activity_name = "Unknown Club"
    email = "ghost@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )
    result = response.json()

    # Assert
    assert response.status_code == 404
    assert result["detail"] == "Activity not found"


def test_remove_invalid_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    email = "missing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )
    result = response.json()

    # Assert
    assert response.status_code == 404
    assert result["detail"] == "Participant not found"
