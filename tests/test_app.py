import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(scope="function")
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(snapshot))


def test_get_activities_returns_available_options(client):
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"], "Expected existing participants in Chess Club"


def test_signup_adds_new_participant(client):
    new_email = "newstudent@mergington.edu"

    response = client.post(
        f"/activities/{quote('Chess Club', safe='')}/signup",
        params={"email": new_email},
    )

    assert response.status_code == 200
    assert new_email in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    existing_email = activities["Chess Club"]["participants"][0]

    response = client.post(
        f"/activities/{quote('Chess Club', safe='')}/signup",
        params={"email": existing_email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_success(client):
    email_to_remove = activities["Chess Club"]["participants"][0]

    response = client.delete(
        f"/activities/{quote('Chess Club', safe='')}/participants/{quote(email_to_remove, safe='')}"
    )

    assert response.status_code == 200
    assert email_to_remove not in client.get("/activities").json()["Chess Club"]["participants"]


def test_remove_participant_not_found(client):
    response = client.delete(
        f"/activities/{quote('Chess Club', safe='')}/participants/{quote('not_present@mergington.edu', safe='')}"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"
