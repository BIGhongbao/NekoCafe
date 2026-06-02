from fastapi.testclient import TestClient

from src.main import RESERVATIONS, app


client = TestClient(app)


def setup_function():
    RESERVATIONS.clear()


def test_healthz_returns_ok():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["service"] == "reservation-service"


def test_create_and_get_reservation():
    response = client.post(
        "/reservations",
        json={
            "member_id": "m001",
            "store_id": "store-bj-001",
            "table_id": "t08",
            "reserved_at": "2026-06-05T18:30:00+08:00",
            "party_size": 2,
        },
    )

    assert response.status_code == 201
    reservation_id = response.json()["id"]

    detail = client.get(f"/reservations/{reservation_id}")
    assert detail.status_code == 200
    assert detail.json()["status"] == "CONFIRMED"


def test_checkin_changes_status():
    created = client.post(
        "/reservations",
        json={
            "member_id": "m001",
            "store_id": "store-bj-001",
            "table_id": "t08",
            "reserved_at": "2026-06-05T18:30:00+08:00",
            "party_size": 2,
        },
    ).json()

    checked_in = client.post(f"/reservations/{created['id']}/checkin")
    assert checked_in.status_code == 200
    assert checked_in.json()["status"] == "CHECKED_IN"


def test_unknown_reservation_returns_404():
    response = client.get("/reservations/not-exist")
    assert response.status_code == 404
