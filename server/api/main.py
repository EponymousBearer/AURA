# api/main.py
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from api.schemas import CultureReportRequest, AnalyzeResponse
from agent.graph import build_graph, GraphState

from api.schemas import (
    CultureReportRequest,
    AnalyzeResponse,
)


app = FastAPI(title="AURA", version="1.0")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GRAPH = build_graph()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: CultureReportRequest):
    # Run graph
    state = GraphState(payload=payload, debug={})
    out = GRAPH.invoke(state)
    
    return AnalyzeResponse(
        status=out["status"],
        parsed_report=out["parsed_report"].model_dump(),
        ranked_options=out.get("ranked_options", []),
        recommendation=out["recommendation"].model_dump(),
        safety_note=out.get("safety_note"),
        debug=out.get("debug") if payload.debug else None,
    )