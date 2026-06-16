import pytest


pytestmark = pytest.mark.unit


def test_healthz_and_readyz(member_client):
    assert member_client.get("/healthz").json()["service"] == "member-service"
    ready = member_client.get("/readyz")
    assert ready.status_code == 200
    assert ready.json()["dependencies"]["database"] == "mock"


def test_get_member_masks_phone(member_client):
    response = member_client.get("/members/m001")
    assert response.status_code == 200
    body = response.json()
    assert body["nickname"] == "NekoFan"
    assert body["phone_masked"] == "138****2703"
    assert "13800002703" not in str(body)


def test_unknown_member_returns_404(member_client):
    response = member_client.get("/members/m999")
    assert response.status_code == 404
    assert response.json()["detail"] == "member not found"


def test_get_benefits_calculates_next_level_points(member_client):
    response = member_client.get("/members/m001/benefits")
    assert response.status_code == 200
    assert response.json()["points"] == 1280
    assert response.json()["next_level_points"] == 720


def test_next_level_points_never_negative(member_module, member_client):
    member_module.MEMBERS["m003"] = member_module.Member(
        id="m003",
        nickname="TopMember",
        phone_masked="137****0000",
        level="Platinum",
        points=2500,
        coupons=1,
        marketing_consent=True,
    )
    response = member_client.get("/members/m003/benefits")
    assert response.status_code == 200
    assert response.json()["next_level_points"] == 0


def test_redeem_coupon_decreases_coupon_count(member_client):
    response = member_client.post("/members/m001/coupons/redeem", headers={"x-trace-id": "trace-coupon"})
    assert response.status_code == 200
    assert response.json()["coupons"] == 2


def test_redeem_coupon_until_none_then_conflict(member_client):
    assert member_client.post("/members/m001/coupons/redeem").json()["coupons"] == 2
    assert member_client.post("/members/m001/coupons/redeem").json()["coupons"] == 1
    assert member_client.post("/members/m001/coupons/redeem").json()["coupons"] == 0
    response = member_client.post("/members/m001/coupons/redeem")
    assert response.status_code == 409
    assert response.json()["detail"] == "no coupons available"


def test_member_with_zero_coupon_cannot_redeem(member_client):
    response = member_client.post("/members/m002/coupons/redeem")
    assert response.status_code == 409
    assert response.json()["detail"] == "no coupons available"


@pytest.mark.parametrize("granted", [True, False])
def test_update_marketing_consent(member_client, granted):
    response = member_client.put("/members/m001/marketing-consent", json={"granted": granted})
    assert response.status_code == 200
    assert response.json()["marketing_consent"] is granted


def test_invalid_marketing_consent_payload_returns_422(member_client):
    response = member_client.put("/members/m001/marketing-consent", json={"granted": "not-a-bool"})
    assert response.status_code == 422


def test_metrics_endpoint_exposes_prometheus_text(member_client):
    response = member_client.get("/metrics")
    assert response.status_code == 200
    assert "nekocafe_http_requests_total" in response.text

