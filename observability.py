# observability.py
import time
from typing import Any, Dict, List

LOGS: List[Dict[str, Any]] = []
METRICS: Dict[str, int] = {"vision": 0, "rag": 0, "plan": 0, "judge": 0}

def log(agent: str, action: str, detail: Any):
    entry = {"ts": time.time(), "agent": agent, "action": action, "detail": detail}
    LOGS.append(entry)

def get_logs():
    return LOGS.copy()

def metric(name: str, increment: int = 1):
    METRICS[name] = METRICS.get(name, 0) + increment

def get_metrics():
    return METRICS.copy()
