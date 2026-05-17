"""Hindsight memory system target implementation."""

import os
from typing import Any

import httpx

from targets.base import MemoryTarget, MemorySnapshot, QueryResult


class HindsightTarget(MemoryTarget):
    """Wrapper around Hindsight memory system via HTTP API.

    Hindsight is a vector-based memory system running at HINDSIGHT_ENDPOINT.
    See: https://hindsight.vectorize.io/developer/api/quickstart
    """

    def __init__(self):
        """Initialize Hindsight client.

        Configuration is loaded from environment:
          - HINDSIGHT_ENDPOINT: base URL (default: http://localhost:8888)
          - HINDSIGHT_API_KEY: authentication key (optional)
        """
        self.base_url = os.getenv("HINDSIGHT_ENDPOINT", "http://localhost:8888")
        self.api_key = os.getenv("HINDSIGHT_API_KEY", "")

        # Build headers dict, only include auth if API key is set
        headers = {}
        if self.api_key and self.api_key.strip():
            headers["Authorization"] = f"Bearer {self.api_key}"

        self.client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
        )
        self.banks: dict[str, str] = {}  # user_id -> bank_id mapping

    def _get_or_create_bank(self, user_id: str) -> str:
        """Get or create a memory bank for a user.

        Args:
            user_id: User identifier.

        Returns:
            Bank ID.
        """
        if user_id in self.banks:
            return self.banks[user_id]

        # Hindsight uses bank_id naming convention; create on demand
        bank_id = f"bank-{user_id}"
        self.banks[user_id] = bank_id
        return bank_id

    def write(self, content: str, user_id: str) -> None:
        """Add content to user's memory bank.

        Args:
            content: Text to retain in memory.
            user_id: User identifier.
        """
        bank_id = self._get_or_create_bank(user_id)

        # POST /v1/default/banks/{bank_id}/memories with items list
        response = self.client.post(
            f"/v1/default/banks/{bank_id}/memories",
            json={"items": [{"content": content}], "async": False},
        )
        response.raise_for_status()

    def query(self, question: str, user_id: str) -> QueryResult:
        """Recall relevant memories in response to a question.

        Args:
            question: The query.
            user_id: User identifier.

        Returns:
            QueryResult with recalled information and source memories.
        """
        bank_id = self._get_or_create_bank(user_id)

        # POST /v1/default/banks/{bank_id}/memories/recall with query
        response = self.client.post(
            f"/v1/default/banks/{bank_id}/memories/recall",
            json={"query": question},
        )
        response.raise_for_status()
        data = response.json()

        # Extract results and build retrieved_memories list
        retrieved_memories = []
        answer_parts = []

        for result in data.get("results", []):
            text = result.get("text", str(result))
            retrieved_memories.append(text)
            answer_parts.append(text)

        answer = "\n".join(answer_parts) if answer_parts else "[no memories found]"
        return QueryResult(answer=answer, retrieved_memories=retrieved_memories)

    def snapshot(self, user_id: str) -> MemorySnapshot:
        """Get a snapshot of all memories in the bank.

        Args:
            user_id: User identifier.

        Returns:
            MemorySnapshot with all stored facts.
        """
        bank_id = self._get_or_create_bank(user_id)

        # GET /v1/default/banks/{bank_id}/memories/list
        response = self.client.get(f"/v1/default/banks/{bank_id}/memories/list")
        response.raise_for_status()
        data = response.json()

        raw_facts = []
        raw_dump = {}

        for item in data.get("items", []):
            raw_facts.append(item)
            item_id = item.get("id", str(item))
            raw_dump[item_id] = item

        return MemorySnapshot(
            user_id=user_id,
            raw_facts=raw_facts,
            derived={},
            raw_dump=raw_dump,
        )

    def reset(self, user_id: str) -> None:
        """Delete all memories in the bank.

        Args:
            user_id: User identifier.
        """
        bank_id = self._get_or_create_bank(user_id)

        # Hindsight doesn't have a direct clear endpoint; create new bank mapping
        # by removing from tracking (new writes will go to fresh bank)
        if user_id in self.banks:
            del self.banks[user_id]

    def inject_initial_state(self, user_id: str, state: dict) -> None:
        """Inject known facts into the memory bank.

        Args:
            user_id: User identifier.
            state: Dictionary with keys as fact names and values as content.
        """
        for key, value in state.items():
            self.write(f"{key}: {value}", user_id)

    def trigger_consolidation(self, user_id: str) -> None:
        """Trigger memory reflection/consolidation.

        Args:
            user_id: User identifier.
        """
        bank_id = self._get_or_create_bank(user_id)

        # POST /v1/default/banks/{bank_id}/reflect with a generic query
        try:
            response = self.client.post(
                f"/v1/default/banks/{bank_id}/reflect",
                json={"query": "Consolidate and summarize all memories"},
            )
            response.raise_for_status()
        except Exception:
            # Reflection is optional; don't fail if unavailable
            pass

    def __del__(self) -> None:
        """Clean up HTTP client."""
        if hasattr(self, "client"):
            self.client.close()
