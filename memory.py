# memory.py
import uuid
import time
import json
from typing import Dict, Any, List
from sentence_transformers import SentenceTransformer
import numpy as np

class InMemorySessionService:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create(self, user_id: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        sid = str(uuid.uuid4())
        self.sessions[sid] = {
            "session_id": sid,
            "user_id": user_id,
            "profile": profile,
            "created_at": time.time(),
            "conversation_history": [],
            "paused_ops": []
        }
        return self.sessions[sid]

    def get(self, sid: str) -> Dict[str, Any]:
        return self.sessions.get(sid)

class VectorStore:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.docs: List[Dict[str, Any]] = []

    def add(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        emb = self.model.encode(text, convert_to_numpy=True)
        entry = {"text": text, "embedding": emb, "metadata": metadata or {}}
        self.docs.append(entry)
        return entry

    def query(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.docs:
            return []
        qvec = self.model.encode(query, convert_to_numpy=True)
        sims = [float(np.dot(qvec, d["embedding"])) for d in self.docs]
        idxs = np.argsort(sims)[::-1][:top_k]
        return [self.docs[i] for i in idxs]
