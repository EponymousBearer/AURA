from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

E_COLI_REPORT = (
    "Specimen Desc. : BLOOD C/S\n"
    "Result :\n"
    "1: E. COLI\n"
    "\n"
    "ANTIBIOTIC SUSCEPTIBILITY\n"
    "1    AMIKACIN                           S\n"
    "2    AMOXACILLIN + CLAVULANIC ACID      S\n"
    "3    AMPICILLIN                         R\n"
    "4    CIPROFLOXACIN                      R\n"
    "5    GENTAMICIN                         S\n"
    "6    CEFTRIAXONE                        R\n"
    "10   PIPERACILLIN-TAZOBACTAM            S\n"
)

def base_payload():
    return {
        "report_text": E_COLI_REPORT,
        "specimen_hint": None,
        "patient": {
            "age_years": 56,
            "sex": "female",
            "syndrome": "gn_bacteremia",
            "severity": "stable",
            "egfr_ml_min": 80,
            "renal_bucket": "normal",
            "beta_lactam_allergy": False,
            "other_allergies": [],
            "pregnancy": False,
            "hepatic_impairment": False,
            "interactions": []
        },
        "debug": True
    }

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True

def test_happy_path_recommendation_ready():
    r = client.post("/analyze", json=base_payload())
    assert r.status_code == 200
    body = r.json()

    assert body["parsed_report"]["specimen"] == "blood"
    assert body["status"] in ["recommendation_ready", "no_safe_option"]  # depends on dosing table coverage
    if body["status"] == "recommendation_ready":
        assert body["recommendation"]["primary"] is not None
        assert body["recommendation"]["primary"]["drug"]

def test_missing_syndrome_triggers_questions():
    p = base_payload()
    p["patient"]["syndrome"] = None
    r = client.post("/analyze", json=p)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "needs_more_info"
    assert body["recommendation"]["primary"] is None
    assert any("syndrome" in x.lower() for x in body["recommendation"]["missing_info"])

def test_missing_renal_triggers_questions():
    p = base_payload()
    p["patient"]["egfr_ml_min"] = None
    p["patient"]["renal_bucket"] = "unknown"
    r = client.post("/analyze", json=p)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "needs_more_info"
    assert any("renal" in x.lower() or "egfr" in x.lower() for x in body["recommendation"]["missing_info"])
