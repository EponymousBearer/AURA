from services.parser import parse_report
from api.schemas import SpecimenType, SIR

def test_blood_report_ecoli():
    text = open("tests/cases/case1_ecoli_blood.txt", "r", encoding="utf-8").read()
    parsed = parse_report(text)

    assert parsed.specimen == SpecimenType.blood
    assert len(parsed.organisms) >= 1
    assert parsed.organisms[0].organism.lower() in ["e. coli", "e. coli"]

    # Confirm a few key AST results exist
    drugs = {x.drug.lower(): x.sir for x in parsed.organisms[0].ast}

    assert "amikacin" in drugs and drugs["amikacin"] == SIR.susceptible
    assert "ampicillin" in drugs and drugs["ampicillin"] == SIR.resistant
    assert "ceftriaxone" in drugs and drugs["ceftriaxone"] == SIR.resistant
    assert "piperacillin-tazobactam" in drugs and drugs["piperacillin-tazobactam"] == SIR.susceptible
