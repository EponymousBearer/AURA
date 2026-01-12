from services.parser import parse_report

text = """Specimen Desc. : BLOOD C/S
Result :
1: E. COLI
ANTIBIOTIC SUSCEPTIBILITY
1 AMIKACIN S
2 AMPICILLIN R
10 PIPERACILLIN-TAZOBACTAM S
"""

p = parse_report(text)
print(p)
