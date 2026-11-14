import pytest

from drones import reset_drone
from index import app


@pytest.fixture
def client():
    reset_drone()
    yield app.test_client()
    reset_drone()


def post(client, path, **body):
    return client.post(path, json=body)


def test_info(client):
    data = client.get("/api/drone_info").get_json()
    assert data["name"] == "Simulator" and "video" in data["capabilities"]
    assert data["simulated"] is True and data["max_altitude"] == 10.0


def test_takeoff_status_land(client):
    assert post(client, "/api/takeoff").get_json()["status"] == "success"
    status = client.get("/api/drone_status").get_json()
    assert status["is_flying"] and status["battery_level"] <= 100
    assert status["sequence_running"] is False
    assert post(client, "/api/land").get_json()["status"] == "success"


def test_takeoff_twice_is_409(client):
    post(client, "/api/takeoff")
    r = post(client, "/api/takeoff")
    assert r.status_code == 409 and r.get_json()["status"] == "error"


def test_legacy_direction_control(client):
    post(client, "/api/takeoff")
    assert post(client, "/api/control", direction="left", speed=50).status_code == 200
    assert post(client, "/api/control", direction="sideways").status_code == 400
    assert post(client, "/api/control", direction="up", speed="fast").status_code == 400


def test_axis_control_and_validation(client):
    post(client, "/api/takeoff")
    assert post(client, "/api/control", forward=30, yaw=-20).status_code == 200
    assert post(client, "/api/control", forward="x").status_code == 400


def test_battery_and_emergency(client):
    assert 0 <= client.get("/api/battery").get_json()["battery_level"] <= 100
    post(client, "/api/takeoff")
    assert post(client, "/api/emergency_stop").status_code == 200
    assert not client.get("/api/drone_status").get_json()["is_flying"]


def test_video_feed_streams_jpeg(client):
    r = client.get("/api/video_feed", buffered=False)
    assert r.mimetype == "multipart/x-mixed-replace"
    chunk = next(iter(r.response))
    assert b"image/jpeg" in chunk and b"\xff\xd8" in chunk


def test_unknown_drone_type(monkeypatch):
    reset_drone()
    monkeypatch.setenv("DRONE_TYPE", "nope")
    r = app.test_client().get("/api/drone_info")
    assert r.status_code == 409 and "Unknown DRONE_TYPE" in r.get_json()["message"]
