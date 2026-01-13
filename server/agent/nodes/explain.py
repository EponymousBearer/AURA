# agent/nodes/explain.py
from __future__ import annotations
from typing import Dict, Any

from agent.state import GraphState
from langchain_groq import ChatGroq
from api.schemas import RecommendationPackage


llm = ChatGroq(
    model="llama-3.1-8b-instant",  # Groq hosted Llama 3.1 8B
    temperature=0.2,
)

EXPLANATION_SYSTEM_PROMPT = """You are a medical expert specializing in antibiotic recommendations and resistance patterns.
Provide a clear, evidence-based explanation of the recommended antibiotic regimen, including:
1. Why this drug was selected based on susceptibility
2. How the dosing and route are appropriate
3. Why alternatives were not chosen
4. Any important considerations or monitoring needed

Keep the explanation concise and clinically focused."""

def explain_node(state: GraphState) -> Dict[str, Any]:
    rec: RecommendationPackage | None = state.get("recommendation")
    parsed = state.get("parsed_report")
    ranked = state.get("ranked_options", [])

    if rec is None or rec.primary is None or parsed is None:
        return {}  # nothing to explain

    # Build structured input for the LLM
    explanation_input = f"""
Organism: {parsed.organisms[0].organism}
Specimen: {parsed.specimen}

Primary regimen:
- Drug: {rec.primary.drug}
- Route: {rec.primary.route}
- Dose: {rec.primary.dose}
- Frequency: {rec.primary.frequency}
- Duration: {rec.primary.duration}

Alternatives:
{', '.join([a.drug for a in rec.alternatives]) or 'None'}

Susceptibility summary:
{', '.join([f"{r.drug}: {r.sir_summary}" for r in ranked])}
"""

    response = llm.invoke([
        {"role": "system", "content": EXPLANATION_SYSTEM_PROMPT},
        {"role": "user", "content": explanation_input},
    ])

    explanation_text = response.content if isinstance(response.content, str) else response.content[0]
    explanation_text = explanation_text.strip() if isinstance(explanation_text, str) else str(explanation_text).strip()

    # Append explanation safely
    rec.rationale.append(explanation_text)

    return {"recommendation": rec}
