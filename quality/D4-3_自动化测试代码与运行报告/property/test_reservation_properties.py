import pytest
from hypothesis import HealthCheck, given, settings, strategies as st


pytestmark = pytest.mark.property


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.integers(min_value=1, max_value=8))
def test_valid_party_size_is_accepted(reservation_client, valid_reservation_payload, party_size):
    response = reservation_client.post(
        "/reservations",
        json={**valid_reservation_payload, "party_size": party_size},
    )
    assert response.status_code == 201
    assert response.json()["party_size"] == party_size


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.one_of(st.integers(max_value=0), st.integers(min_value=9, max_value=100)))
def test_invalid_party_size_is_rejected(reservation_client, valid_reservation_payload, party_size):
    response = reservation_client.post(
        "/reservations",
        json={**valid_reservation_payload, "party_size": party_size},
    )
    assert response.status_code == 422


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.text(min_size=0, max_size=80))
def test_special_request_round_trip(reservation_client, valid_reservation_payload, special_request):
    response = reservation_client.post(
        "/reservations",
        json={**valid_reservation_payload, "special_request": special_request},
    )
    assert response.status_code == 201
    assert response.json()["special_request"] == special_request
