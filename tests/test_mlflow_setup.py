"""
Smoke tests for MLflow server configuration — Story 7.1.

These tests verify the MLflow setup WITHOUT requiring a running server.
They check:
  - mlflow package can be imported
  - mlflow.set_tracking_uri() accepts a URI without error
  - mlflow.set_experiment() API is callable (function exists)
  - docker-compose.yml contains an mlflow service block
  - .env.example documents MLFLOW_TRACKING_URI
"""

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# MLflow import smoke test
# ---------------------------------------------------------------------------


def test_mlflow_package_importable():
    """MLflow must be installed (added to requirements.txt in Task 1.1)."""
    try:
        import mlflow  # noqa: F401

        assert True
    except ImportError:
        pytest.fail("mlflow is not installed — run: pip install mlflow==2.13.0")


def test_mlflow_set_tracking_uri_accepts_uri():
    """mlflow.set_tracking_uri() should accept a URI string without error."""
    import mlflow

    # Calling with a fake URI should not raise — it only fails when actually connecting
    mlflow.set_tracking_uri("http://localhost:5000")
    assert mlflow.get_tracking_uri() == "http://localhost:5000"


def test_mlflow_set_experiment_api_exists():
    """mlflow.set_experiment() function must exist (API surface check)."""
    import mlflow

    assert callable(mlflow.set_experiment)


def test_mlflow_sklearn_module_importable():
    """mlflow.sklearn is required for log_model() in Story 7.2."""
    try:
        import mlflow.sklearn  # noqa: F401

        assert True
    except ImportError:
        pytest.fail("mlflow.sklearn not importable — check mlflow installation")


# ---------------------------------------------------------------------------
# docker-compose.yml configuration checks
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent
COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"


def test_docker_compose_has_mlflow_service():
    """docker-compose.yml must contain an 'mlflow:' service block."""
    assert COMPOSE_FILE.exists(), "docker-compose.yml not found at project root"
    content = COMPOSE_FILE.read_text()
    assert (
        "mlflow:" in content
    ), "No 'mlflow:' service found in docker-compose.yml — check Story 7.1 Task 1.2"


def test_docker_compose_mlflow_uses_port_5000():
    """MLflow service must map port 5000:5000."""
    content = COMPOSE_FILE.read_text()
    # Check port mapping exists
    assert (
        '"5000:5000"' in content or "'5000:5000'" in content or "5000:5000" in content
    ), "Port 5000:5000 mapping not found in docker-compose.yml for mlflow service"


def test_docker_compose_mlflow_has_postgres_backend():
    """MLflow backend-store-uri must reference PostgreSQL."""
    content = COMPOSE_FILE.read_text()
    assert (
        "backend-store-uri" in content
    ), "--backend-store-uri not found in docker-compose.yml mlflow command"
    assert "postgresql" in content, "PostgreSQL backend store URI not configured for MLflow"


def test_docker_compose_mlflow_has_s3_artifact_root():
    """MLflow default-artifact-root must reference S3."""
    content = COMPOSE_FILE.read_text()
    assert "default-artifact-root" in content, "--default-artifact-root not found in mlflow command"
    assert "s3://" in content, "S3 artifact root not configured for MLflow"


def test_docker_compose_mlflow_depends_on_db():
    """MLflow service must declare depends_on: db."""
    content = COMPOSE_FILE.read_text()
    # Check that mlflow section comes after mlflow: and before next top-level service
    mlflow_idx = content.find("mlflow:")
    assert mlflow_idx != -1, "mlflow service not found"
    mlflow_section = content[mlflow_idx : mlflow_idx + 1000]
    assert "depends_on" in mlflow_section, "MLflow service missing depends_on in docker-compose.yml"
    assert "db" in mlflow_section, "MLflow service does not depend on 'db' service"


# ---------------------------------------------------------------------------
# .env.example documentation checks
# ---------------------------------------------------------------------------

ENV_EXAMPLE = PROJECT_ROOT / ".env.example"


def test_env_example_has_mlflow_tracking_uri():
    """.env.example must document MLFLOW_TRACKING_URI."""
    assert ENV_EXAMPLE.exists(), ".env.example not found at project root"
    content = ENV_EXAMPLE.read_text()
    assert "MLFLOW_TRACKING_URI" in content, "MLFLOW_TRACKING_URI not documented in .env.example"


def test_env_example_mlflow_uses_port_5000():
    """MLFLOW_TRACKING_URI in .env.example must use port 5000."""
    content = ENV_EXAMPLE.read_text()
    assert "5000" in content, "Port 5000 not referenced in MLFLOW_TRACKING_URI in .env.example"
