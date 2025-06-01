from datetime import datetime
from langchain.agents import tool


@tool
def get_current_time() -> dict:
    """
    Return the current UTC time in ISO‑8601 format.
    Example → {"utc": "2025‑05‑21T06:42:00Z"}
    """
    return {"utc": datetime.utcnow().isoformat() + "Z"}
