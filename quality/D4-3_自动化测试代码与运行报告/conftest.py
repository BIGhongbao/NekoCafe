from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from prometheus_client import REGISTRY


def find_d3_repo() -> Path:
    env_repo = os.getenv("D3_REPO")
    if env_repo:
        return Path(env_repo)

    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "services" / "reservation" / "src" / "main.py").exists():
            return parent

    for parent in here.parents:
        candidate = parent / "实验三_DevOps流水线与容器化部署" / "实验三_产出" / "D3-2_源代码与配置仓库"
        if (candidate / "services" / "reservation" / "src" / "main.py").exists():
            return candidate

    raise FileNotFoundError("Cannot locate D3-2 source repository. Set D3_REPO to the repository path.")


D3_REPO = find_d3_repo()
RESERVATION_MAIN = D3_REPO / "services" / "reservation" / "src" / "main.py"
MEMBER_MAIN = D3_REPO / "services" / "member" / "src" / "main.py"


def _reset_nekocafe_metrics() -> None:
    """Avoid prometheus duplicate metric registration when loading both services."""
    for collector, names in list(REGISTRY._collector_to_names.items()):
        if any(name.startswith("nekocafe_http_") for name in names):
            try:
                REGISTRY.unregister(collector)
            except KeyError:
                pass


def load_service_module(name: str, path: Path):
    _reset_nekocafe_metrics()
    module_name = f"d4_{name}_main"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load service module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def reservation_module():
    module = load_service_module("reservation", RESERVATION_MAIN)
    module.RESERVATIONS.clear()
    return module


@pytest.fixture()
def reservation_client(reservation_module):
    return TestClient(reservation_module.app)


@pytest.fixture()
def member_module():
    module = load_service_module("member", MEMBER_MAIN)
    module.MEMBERS.clear()
    module.MEMBERS["m001"] = module.Member(
        id="m001",
        nickname="NekoFan",
        phone_masked="138****2703",
        level="Gold",
        points=1280,
        coupons=3,
        marketing_consent=True,
    )
    module.MEMBERS["m002"] = module.Member(
        id="m002",
        nickname="LatteCat",
        phone_masked="139****6618",
        level="Silver",
        points=520,
        coupons=0,
        marketing_consent=False,
    )
    return module


@pytest.fixture()
def member_client(member_module):
    return TestClient(member_module.app)


@pytest.fixture()
def valid_reservation_payload():
    return {
        "member_id": "m001",
        "store_id": "store-bj-001",
        "table_id": "t08",
        "reserved_at": "2026-06-05T18:30:00+08:00",
        "party_size": 2,
        "special_request": "靠窗，低糖甜品",
    }
