import json
from pathlib import Path

import pytest


pytestmark = pytest.mark.contract


def test_member_benefits_contract(member_client):
    contract = json.loads((Path(__file__).with_name("member-benefits-contract.json")).read_text(encoding="utf-8"))
    interaction = contract["interactions"][0]
    response = member_client.get(interaction["request"]["path"])
    assert response.status_code == interaction["response"]["status"]
    body = response.json()
    for field in interaction["response"]["requiredFields"]:
        assert field in body


def test_reservation_create_contract(reservation_client, valid_reservation_payload):
    contract = json.loads((Path(__file__).with_name("reservation-contract.json")).read_text(encoding="utf-8"))
    interaction = contract["interactions"][0]
    response = reservation_client.post(interaction["request"]["path"], json=valid_reservation_payload)
    assert response.status_code == interaction["response"]["status"]
    body = response.json()
    for field in interaction["response"]["requiredFields"]:
        assert field in body

