"""Base abstraction for memory systems under test."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class MemorySnapshot:
    """Complete dump of a user's memory state at one point in time."""

    user_id: str
    raw_facts: list[dict]
    derived: dict[str, Any]
    raw_dump: dict


@dataclass
class QueryResult:
    """What the agent returns to a user query."""

    answer: str
    retrieved_memories: list[dict]


class MemoryTarget(ABC):
    """Unified interface for memory systems under test.

    All methods are synchronous. Implementations may wrap async APIs internally
    if needed (e.g., via asyncio.run).
    """

    @abstractmethod
    def write(self, content: str, user_id: str) -> None:
        """User sends a message; system decides what to remember.

        Args:
            content: Raw text input from the user or attacker.
            user_id: Identifier for the user whose memory to write to.
        """

    @abstractmethod
    def query(self, question: str, user_id: str) -> QueryResult:
        """Agent answers a question using its memory.

        Args:
            question: The user's query.
            user_id: Identifier for the user whose memory to query.

        Returns:
            QueryResult with the agent's answer and list of retrieved memories.
        """

    @abstractmethod
    def snapshot(self, user_id: str) -> MemorySnapshot:
        """Dump the current memory state for diff and judging.

        Returns:
            MemorySnapshot containing raw facts, derived data, and full state dump.
        """

    @abstractmethod
    def reset(self, user_id: str) -> None:
        """Wipe all memory for this user.

        Args:
            user_id: Identifier for the user whose memory to reset.
        """

    @abstractmethod
    def inject_initial_state(self, user_id: str, state: dict) -> None:
        """Set memory to a known starting state for a level.

        Args:
            user_id: Identifier for the user.
            state: Dictionary of facts to inject (format depends on target implementation).
        """

    @abstractmethod
    def trigger_consolidation(self, user_id: str) -> None:
        """Force LLM summarization/consolidation if applicable.

        Some memory systems (e.g., those with rollup/derive steps) may batch
        memory consolidation. This method triggers it manually for testing.

        Args:
            user_id: Identifier for the user.
        """
