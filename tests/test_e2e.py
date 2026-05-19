"""End-to-end tests for the hiring agent workflow.

Run with: python tests/test_e2e.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflow.graph import run_workflow


def test_candidate_yyf():
    """Test candidate: strong match (YYF resume)."""
    input_path = Path(__file__).parent.parent / "examples" / "candidate_yyf.md"
    text = input_path.read_text(encoding="utf-8")

    result = run_workflow(text, input_type="candidate")

    assert result is not None
    assert "extracted_data" in result
    assert "analysis" in result
    assert "recommendation" in result

    # Check tags
    tags = result["analysis"].get("tags", [])
    assert any("AI" in t or "Agent" in t or "LangGraph" in t for t in tags), f"Expected AI-related tags, got: {tags}"

    # Check match score (should be 85-90)
    score = result["analysis"].get("match_score", 0)
    assert 70 <= score <= 95, f"Expected score 70-95, got: {score}"

    print(f"[PASS] candidate_yyf - score: {score}, tags: {tags}")


def test_candidate_frontend():
    """Test candidate: weak match (frontend only)."""
    input_path = Path(__file__).parent.parent / "examples" / "candidate_frontend.md"
    text = input_path.read_text(encoding="utf-8")

    result = run_workflow(text, input_type="candidate")

    assert result is not None
    assert "analysis" in result

    # Check match score (should be 30-40)
    score = result["analysis"].get("match_score", 0)
    assert 20 <= score <= 50, f"Expected score 20-50, got: {score}"

    # Check risk points
    risk_points = result["analysis"].get("risk_points", [])
    assert any("AI" in r.get("point", "") or "大模型" in r.get("point", "") for r in risk_points), \
        f"Expected AI-related risk, got: {risk_points}"

    print(f"[PASS] candidate_frontend - score: {score}")


def test_project_vtdemo():
    """Test project: VT-Demo."""
    input_path = Path(__file__).parent.parent / "examples" / "project_vtdemo.md"
    text = input_path.read_text(encoding="utf-8")

    result = run_workflow(text, input_type="project")

    assert result is not None
    assert "extracted_data" in result
    assert "analysis" in result

    # Check tags
    tags = result["analysis"].get("tags", [])
    assert any("RAG" in t or "Agent" in t or "能源" in t for t in tags), f"Expected RAG/Agent tags, got: {tags}"

    # Check match score (should be 90)
    score = result["analysis"].get("match_score", 0)
    assert 80 <= score <= 98, f"Expected score 80-98, got: {score}"

    print(f"[PASS] project_vtdemo - score: {score}, tags: {tags}")


if __name__ == "__main__":
    print("Running e2e tests...")
    print()

    try:
        test_candidate_yyf()
    except Exception as e:
        print(f"[FAIL] candidate_yyf: {e}")

    try:
        test_candidate_frontend()
    except Exception as e:
        print(f"[FAIL] candidate_frontend: {e}")

    try:
        test_project_vtdemo()
    except Exception as e:
        print(f"[FAIL] project_vtdemo: {e}")

    print()
    print("Tests completed.")