# api/settings.py
from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "AURA")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
