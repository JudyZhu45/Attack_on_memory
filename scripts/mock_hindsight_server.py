#!/usr/bin/env python
"""Mock Hindsight API server for testing without full Docker image."""

import json
from typing import Dict, List, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn


# Data models
class RetainRequest(BaseModel):
    bank_id: str
    content: str


class RecallRequest(BaseModel):
    bank_id: str
    query: str


class ReflectRequest(BaseModel):
    bank_id: str
    query: str


# In-memory storage
banks: Dict[str, Dict[str, Any]] = {}


def create_app():
    app = FastAPI(title="Mock Hindsight API", version="0.1.0")

    # In-memory storage for observations
    observations: Dict[str, List[Dict]] = {}

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

    @app.post("/v1/retain")
    async def retain(request: RetainRequest):
        """Store a fact (retain)."""
        bank_id = request.bank_id
        content = request.content

        if bank_id not in observations:
            observations[bank_id] = []

        # Simple deduplication: check if similar content already exists
        normalized = content.lower()
        for obs in observations[bank_id]:
            if obs["content"].lower() == normalized:
                # Exact duplicate - update existing
                obs["updated_at"] = datetime.utcnow().isoformat()
                return {
                    "status": "merged",
                    "observation_id": obs["id"],
                    "message": "Duplicate observation updated",
                }

        # Check for semantic duplicates (simple heuristic: check key words)
        content_words = set(normalized.split())
        for obs in observations[bank_id]:
            obs_words = set(obs["content"].lower().split())
            if len(content_words & obs_words) / max(len(content_words), len(obs_words)) > 0.6:
                # Semantic duplicate (60% word overlap)
                obs["updated_at"] = datetime.utcnow().isoformat()
                return {
                    "status": "merged",
                    "observation_id": obs["id"],
                    "message": "Semantic duplicate merged",
                }

        # New observation
        observation_id = f"obs_{len(observations[bank_id]) + 1}"
        observations[bank_id].append(
            {
                "id": observation_id,
                "content": content,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
        )

        return {
            "status": "retained",
            "observation_id": observation_id,
            "bank_id": bank_id,
        }

    @app.post("/v1/recall")
    async def recall(request: RecallRequest):
        """Retrieve relevant observations (recall)."""
        bank_id = request.bank_id
        query = request.query

        if bank_id not in observations:
            return {"results": [], "query": query, "bank_id": bank_id}

        # Simple search: return all observations that match query words
        query_words = set(query.lower().split())
        results = []

        for obs in observations[bank_id]:
            obs_words = set(obs["content"].lower().split())
            score = len(query_words & obs_words) / max(len(query_words), 1)

            if score > 0:
                results.append(
                    {
                        "observation_id": obs["id"],
                        "content": obs["content"],
                        "relevance_score": score,
                        "created_at": obs["created_at"],
                    }
                )

        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        return {
            "results": results,
            "query": query,
            "bank_id": bank_id,
            "total_retrieved": len(results),
        }

    @app.post("/v1/reflect")
    async def reflect(request: ReflectRequest):
        """Generate a reflection/response (reflect)."""
        bank_id = request.bank_id
        query = request.query

        if bank_id not in observations or not observations[bank_id]:
            return {
                "reflection": "No observations available to reflect on.",
                "query": query,
                "bank_id": bank_id,
            }

        # Mock reflection: summarize relevant observations
        query_words = set(query.lower().split())
        relevant = []

        for obs in observations[bank_id]:
            obs_words = set(obs["content"].lower().split())
            score = len(query_words & obs_words) / max(len(query_words), 1)
            if score > 0:
                relevant.append(obs["content"])

        if "coffee" in query.lower():
            reflection = (
                "Based on your memories, you love BlueBottle coffee. "
                "I'd recommend checking out their flagship locations or trying their pour-overs."
            )
        elif "rust" in query.lower():
            reflection = "You enjoy Rust programming. It's a great choice for systems programming!"
        else:
            reflection = f"Based on {len(relevant)} observations, I can help with that."

        return {
            "reflection": reflection,
            "observations_considered": len(relevant),
            "query": query,
            "bank_id": bank_id,
        }

    @app.get("/v1/observations")
    async def list_observations(bank_id: str):
        """List all observations in a bank."""
        if bank_id not in observations:
            return {"observations": [], "bank_id": bank_id, "total": 0}

        return {
            "observations": observations[bank_id],
            "bank_id": bank_id,
            "total": len(observations[bank_id]),
        }

    return app


if __name__ == "__main__":
    app = create_app()
    print("=" * 70)
    print("Mock Hindsight API Server")
    print("=" * 70)
    print()
    print("Starting on http://localhost:8888")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")
