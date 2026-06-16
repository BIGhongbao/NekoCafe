from pathlib import Path
import os

import pytest


pytestmark = pytest.mark.integration


def test_docker_compose_file_defines_required_services():
    env_repo = os.getenv("D3_REPO")
    if env_repo:
        repo_root = Path(env_repo)
    else:
        here = Path(__file__).resolve()
        repo_root = next(
            (
                parent for parent in here.parents
                if (parent / "services").exists() and (parent / "docker-compose.yml").exists()
            ),
            None,
        )
        if repo_root is None:
            repo_root = next(
                (
                    parent / "实验三_DevOps流水线与容器化部署" / "实验三_产出" / "D3-2_源代码与配置仓库"
                    for parent in here.parents
                    if (
                        parent / "实验三_DevOps流水线与容器化部署" / "实验三_产出" / "D3-2_源代码与配置仓库" / "docker-compose.yml"
                    ).exists()
                ),
                None,
            )
        if repo_root is None:
            raise FileNotFoundError("Cannot locate docker-compose.yml. Set D3_REPO to the repository path.")
    compose = repo_root / "docker-compose.yml"
    text = compose.read_text(encoding="utf-8")
    assert "reservation-service:" in text
    assert "member-service:" in text
    assert "postgres:" in text
    assert "redis:" in text
    assert "8081:8080" in text
    assert "8082:8080" in text
