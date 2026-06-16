import pytest


pytestmark = pytest.mark.unit


def create_reservation(client, payload):
    response = client.post("/reservations", json=payload, headers={"x-trace-id": "trace-test"})
    assert response.status_code == 201
    return response.json()


def test_healthz_and_readyz(reservation_client):
    assert reservation_client.get("/healthz").json()["service"] == "reservation-service"
    ready = reservation_client.get("/readyz")
    assert ready.status_code == 200
    assert ready.json()["dependencies"]["database"] == "mock"


def test_create_reservation_returns_confirmed_status(reservation_client, valid_reservation_payload):
    created = create_reservation(reservation_client, valid_reservation_payload)
    assert created["id"].startswith("rsv_")
    assert created["status"] == "CONFIRMED"
    assert created["party_size"] == 2
    assert created["special_request"] == "靠窗，低糖甜品"


def test_get_reservation_after_create(reservation_client, valid_reservation_payload):
    created = create_reservation(reservation_client, valid_reservation_payload)
    detail = reservation_client.get(f"/reservations/{created['id']}")
    assert detail.status_code == 200
    assert detail.json()["member_id"] == "m001"


def test_unknown_reservation_returns_404(reservation_client):
    response = reservation_client.get("/reservations/not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "reservation not found"


@pytest.mark.parametrize("party_size", [0, 9, -1])
def test_invalid_party_size_returns_422(reservation_client, valid_reservation_payload, party_size):
    payload = {**valid_reservation_payload, "party_size": party_size}
    response = reservation_client.post("/reservations", json=payload)
    assert response.status_code == 422


def test_party_size_boundaries_are_allowed(reservation_client, valid_reservation_payload):
    for party_size in [1, 8]:
        payload = {**valid_reservation_payload, "party_size": party_size}
        response = reservation_client.post("/reservations", json=payload)
        assert response.status_code == 201
        assert response.json()["party_size"] == party_size


def test_checkin_changes_status(reservation_client, valid_reservation_payload):
    created = create_reservation(reservation_client, valid_reservation_payload)
    response = reservation_client.post(f"/reservations/{created['id']}/checkin")
    assert response.status_code == 200
    assert response.json()["status"] == "CHECKED_IN"


def test_cancel_changes_status(reservation_client, valid_reservation_payload):
    created = create_reservation(reservation_client, valid_reservation_payload)
    response = reservation_client.delete(f"/reservations/{created['id']}")
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_cancelled_reservation_cannot_checkin(reservation_client, valid_reservation_payload):
    created = create_reservation(reservation_client, valid_reservation_payload)
    reservation_client.delete(f"/reservations/{created['id']}")
    response = reservation_client.post(f"/reservations/{created['id']}/checkin")
    assert response.status_code == 409
    assert response.json()["detail"] == "cancelled reservation cannot check in"


def test_checked_in_reservation_cannot_cancel(reservation_client, valid_reservation_payload):
    created = create_reservation(reservation_client, valid_reservation_payload)
    reservation_client.post(f"/reservations/{created['id']}/checkin")
    response = reservation_client.delete(f"/reservations/{created['id']}")
    assert response.status_code == 409
    assert response.json()["detail"] == "checked-in reservation cannot be cancelled"


def test_trace_id_header_is_returned(reservation_client, valid_reservation_payload):
    response = reservation_client.post(
        "/reservations",
        json=valid_reservation_payload,
        headers={"x-trace-id": "trace-d4-001"},
    )
    assert response.status_code == 201
    assert response.headers["x-trace-id"] == "trace-d4-001"


def test_metrics_endpoint_exposes_prometheus_text(reservation_client):
    response = reservation_client.get("/metrics")
    assert response.status_code == 200
    assert "nekocafe_http_requests_total" in response.text

