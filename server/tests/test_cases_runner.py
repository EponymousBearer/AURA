import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

CASES_DIR = Path("tests/cases")


def load_cases():
    files = sorted(CASES_DIR.glob("*.json"))
    if not files:
        raise RuntimeError("No JSON cases found in tests/cases/")
    cases = []
    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            obj = json.load(fp)
            cases.append((f.name, obj))
    return cases


@pytest.mark.parametrize("filename,case", load_cases())
def test_case_runner(filename, case):
    req = case["request"]
    expected_status = case["expected"]["status"]

    r = client.post("/analyze", json=req)
    assert r.status_code == 200, f"{filename} failed HTTP: {r.status_code} {r.text}"

    body = r.json()

    # 1) Status check
    assert body["status"] == expected_status, f"{filename} expected {expected_status}, got {body['status']}"

    # 2) Basic schema sanity
    assert "parsed_report" in body
    assert "recommendation" in body

    # 3) Specimen strictness: if report contains BLOOD C/S, must be blood
    if "BLOOD C/S" in req["report_text"].upper():
        assert body["parsed_report"]["specimen"] == "blood", f"{filename} specimen not blood"

    # 4) If recommendation_ready => primary must exist and must include required fields
    if body["status"] == "recommendation_ready":
        primary = body["recommendation"]["primary"]
        assert primary is not None, f"{filename} expected primary regimen"
        for k in ["drug", "route", "dose", "frequency", "duration", "source"]:
            assert primary.get(k), f"{filename} missing primary.{k}"

        # ranked options should not be empty
        assert len(body.get("ranked_options", [])) > 0, f"{filename} expected ranked_options"

    # 5) Safety behavior: if needs_more_info => primary should be null
    if body["status"] == "needs_more_info":
        assert body["recommendation"]["primary"] is None, f"{filename} needs_more_info should not dose"
        assert len(body["recommendation"].get("missing_info", [])) > 0, f"{filename} missing_info should not be empty"

    # 6) If polymicrobial => needs_review
    if "2:" in req["report_text"]:
        # only assert if the case expects review, otherwise ignore
        if expected_status == "needs_review":
            assert body["status"] == "needs_review"
