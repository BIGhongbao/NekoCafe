from pathlib import Path

import pytest


pytestmark = pytest.mark.integration


def test_docker_compose_file_defines_required_services():
    repo_root = Path(__file__).resolve().parents[3]
    compose = repo_root / "docker-compose.yml"
    text = compose.read_text(encoding="utf-8")
    assert "reservation-service:" in text
    assert "member-service:" in text
    assert "postgres:" in text
    assert "redis:" in text
    assert "8081:8080" in text
    assert "8082:8080" in text
