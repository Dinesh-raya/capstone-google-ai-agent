# mcp.py
import time
import uuid
from typing import Dict, Any, List

PENDING_OPS: Dict[str, Dict[str, Any]] = {}

def start_lro(session_id: str, payload: Dict[str, Any], reason: str = "approval_needed") -> str:
    op_id = str(uuid.uuid4())
    PENDING_OPS[op_id] = {
        "op_id": op_id,
        "session_id": session_id,
        "payload": payload,
        "reason": reason,
        "status": "pending",
        "created": time.time()
    }
    return op_id

def resume_lro(op_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
    if op_id not in PENDING_OPS:
        return {"error": "Invalid op_id"}
    PENDING_OPS[op_id]["status"] = "done"
    PENDING_OPS[op_id]["result"] = result
    PENDING_OPS[op_id]["resumed_at"] = time.time()
    return PENDING_OPS[op_id]

def list_pending() -> List[Dict[str, Any]]:
    return [o for o in PENDING_OPS.values() if o.get("status") == "pending"]
