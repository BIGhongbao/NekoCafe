from fastapi.testclient import TestClient

from src.main import MEMBERS, Member, app


client = TestClient(app)


def setup_function():
    MEMBERS.clear()
    MEMBERS["m001"] = Member(
        id="m001",
        nickname="NekoFan",
        phone_masked="138****2703",
        level="Gold",
        points=1280,
        coupons=3,
        marketing_consent=True,
    )


def test_healthz_returns_ok():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["service"] == "member-service"


def test_get_member_benefits():
    response = client.get("/members/m001/benefits")
    assert response.status_code == 200
    assert response.json()["coupons"] == 3


def test_redeem_coupon_decreases_coupon_count():
    response = client.post("/members/m001/coupons/redeem")
    assert response.status_code == 200
    assert response.json()["coupons"] == 2


def test_unknown_member_returns_404():
    response = client.get("/members/m999")
    assert response.status_code == 404
