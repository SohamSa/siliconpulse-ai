"""Phase 1 smoke tests — repository scaffolding only."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_required_phase1_docs_exist() -> None:
    required = [
        "README.md",
        "ARCHITECTURE.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "LICENSE",
        "IMPLEMENTATION_CHECKLIST.md",
        "docs/product/PRODUCT_REQUIREMENTS.md",
        "docs/product/BUSINESS_PROBLEMS.md",
        "docs/product/USER_PERSONAS.md",
        "docs/product/ROADMAP.md",
        "docs/architecture/SYSTEM_CONTEXT.md",
        "docs/architecture/DATA_FLOW.md",
        "docs/ai/AI_STRATEGY.md",
        "docs/agents/AGENT_DESIGN.md",
        ".env.example",
        ".gitignore",
        "pyproject.toml",
        "Makefile",
        "apps/web/package.json",
    ]
    missing = [path for path in required if not (REPO_ROOT / path).is_file()]
    assert missing == [], f"Missing Phase 1 files: {missing}"


@pytest.mark.unit
def test_env_example_has_no_production_claims() -> None:
    content = (REPO_ROOT / ".env.example").read_text(encoding="utf-8")
    assert "DEVELOPMENT-ONLY" in content or "development-only" in content.lower()
    assert "POSTGRES_PASSWORD" in content
    assert "JWT_SECRET" in content


@pytest.mark.unit
def test_shared_models_package_importable() -> None:
    import shared_models

    assert shared_models.__version__ == "0.1.0"
