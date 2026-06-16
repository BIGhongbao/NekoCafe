import pytest


pytestmark = pytest.mark.integration


def test_reservation_create_lookup_cancel_journey(reservation_client, valid_reservation_payload):
    created = reservation_client.post("/reservations", json=valid_reservation_payload)
    assert created.status_code == 201
    reservation_id = created.json()["id"]

    detail = reservation_client.get(f"/reservations/{reservation_id}")
    assert detail.status_code == 200
    assert detail.json()["status"] == "CONFIRMED"

    cancelled = reservation_client.delete(f"/reservations/{reservation_id}")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "CANCELLED"


def test_member_benefit_coupon_consent_journey(member_client):
    member = member_client.get("/members/m001")
    assert member.status_code == 200
    assert member.json()["marketing_consent"] is True

    benefit = member_client.get("/members/m001/benefits")
    assert benefit.status_code == 200
    before_coupons = benefit.json()["coupons"]

    redeemed = member_client.post("/members/m001/coupons/redeem")
    assert redeemed.status_code == 200
    assert redeemed.json()["coupons"] == before_coupons - 1

    consent = member_client.put("/members/m001/marketing-consent", json={"granted": False})
    assert consent.status_code == 200
    assert consent.json()["marketing_consent"] is False


def test_cross_service_smoke_health(reservation_client, member_client):
    assert reservation_client.get("/healthz").status_code == 200
    assert member_client.get("/healthz").status_code == 200
    assert reservation_client.get("/readyz").status_code == 200
    assert member_client.get("/readyz").status_code == 200

