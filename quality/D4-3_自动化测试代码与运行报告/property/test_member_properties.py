import pytest
from hypothesis import HealthCheck, given, settings, strategies as st


pytestmark = pytest.mark.property


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.integers(min_value=0, max_value=5000))
def test_next_level_points_is_never_negative(member_module, member_client, points):
    member_module.MEMBERS["generated"] = member_module.Member(
        id="generated",
        nickname="Generated",
        phone_masked="136****0000",
        level="Generated",
        points=points,
        coupons=0,
        marketing_consent=False,
    )
    response = member_client.get("/members/generated/benefits")
    assert response.status_code == 200
    assert response.json()["next_level_points"] >= 0


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.integers(min_value=0, max_value=10))
def test_coupon_redeem_never_produces_negative_count(member_module, member_client, coupons):
    member_module.MEMBERS["coupon-user"] = member_module.Member(
        id="coupon-user",
        nickname="CouponUser",
        phone_masked="135****0000",
        level="Silver",
        points=100,
        coupons=coupons,
        marketing_consent=True,
    )
    for _ in range(coupons):
        response = member_client.post("/members/coupon-user/coupons/redeem")
        assert response.status_code == 200
        assert response.json()["coupons"] >= 0
    exhausted = member_client.post("/members/coupon-user/coupons/redeem")
    assert exhausted.status_code == 409
