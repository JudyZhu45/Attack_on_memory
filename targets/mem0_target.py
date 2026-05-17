"""mem0 memory system target implementation."""

import os
from typing import Any

from targets.base import MemoryTarget, MemorySnapshot, QueryResult


class Mem0Target(MemoryTarget):
    """Wrapper around mem0 memory system.

    Uses the mem0ai Python SDK to store and retrieve memories.
    See: https://github.com/mem0ai/mem0
    """

    def __init__(self):
        """Initialize mem0 client.

        Configuration is loaded from environment:
          - OPENAI_API_KEY: for LLM and embeddings
          - MEM0_TELEMETRY: (optional) False to disable telemetry
        """
        from mem0 import Memory

        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-3.5-turbo",
                    "api_key": openai_key,
                },
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small",
                    "api_key": openai_key,
                },
            },
        }
        self.memory = Memory.from_config(config)

    def write(self, content: str, user_id: str) -> None:
        """Add content to user's memory.

        Args:
            content: Text to add to memory.
            user_id: User identifier.
        """
        self.memory.add(content, user_id=user_id)

    def query(self, question: str, user_id: str) -> QueryResult:
        """Query user's memory and return answer.

        Args:
            question: The query to answer.
            user_id: User identifier.

        Returns:
            QueryResult with answer and retrieved memories.
        """
        search_results = self.memory.search(question, filters={"user_id": user_id})

        # Extract memories list from response
        retrieved_memories = []
        answer_parts = []

        if isinstance(search_results, dict) and "results" in search_results:
            results = search_results["results"]
        else:
            results = search_results if isinstance(search_results, list) else []

        for result in results:
            if isinstance(result, dict):
                memory_text = result.get("memory", str(result))
            else:
                memory_text = str(result)
            retrieved_memories.append(memory_text)
            answer_parts.append(memory_text)

        answer = "\n".join(answer_parts) if answer_parts else "[no memories found]"
        return QueryResult(answer=answer, retrieved_memories=retrieved_memories)

    def snapshot(self, user_id: str) -> MemorySnapshot:
        """Get current memory state.

        Args:
            user_id: User identifier.

        Returns:
            MemorySnapshot with all stored facts.
        """
        all_memories = self.memory.get_all(filters={"user_id": user_id})

        # Extract results list from response
        if isinstance(all_memories, dict) and "results" in all_memories:
            memories_list = all_memories["results"]
        else:
            memories_list = all_memories if isinstance(all_memories, list) else []

        # Convert to list of dicts
        raw_facts = []
        raw_dump = {}
        for i, mem in enumerate(memories_list):
            if isinstance(mem, dict):
                raw_facts.append(mem)
                mem_id = mem.get("id", f"mem_{i}")
                raw_dump[mem_id] = mem
            else:
                # If it's an object, try to serialize it
                mem_dict = {"memory": str(mem)}
                raw_facts.append(mem_dict)
                mem_id = f"mem_{i}"
                raw_dump[mem_id] = mem_dict

        return MemorySnapshot(
            user_id=user_id,
            raw_facts=raw_facts,
            derived={},
            raw_dump=raw_dump,
        )

    def reset(self, user_id: str) -> None:
        """Delete all memory for a user.

        Args:
            user_id: User identifier.
        """
        all_memories = self.memory.get_all(filters={"user_id": user_id})

        # Extract results list from response
        if isinstance(all_memories, dict) and "results" in all_memories:
            memories_list = all_memories["results"]
        else:
            memories_list = all_memories if isinstance(all_memories, list) else []

        for mem in memories_list:
            if isinstance(mem, dict):
                mem_id = mem.get("id")
                if mem_id:
                    self.memory.delete(mem_id)

    def inject_initial_state(self, user_id: str, state: dict) -> None:
        """Inject known facts into memory.

        Args:
            user_id: User identifier.
            state: Dictionary with keys as memory fields and values as content to add.
        """
        for key, value in state.items():
            self.memory.add(f"{key}: {value}", user_id=user_id)

    def trigger_consolidation(self, user_id: str) -> None:
        """Trigger memory consolidation (no-op for mem0 if auto).

        mem0 may auto-consolidate; this is a placeholder for manual trigger.

        Args:
            user_id: User identifier.
        """
        # TODO: Check if mem0 has a consolidate/summarize method
        # If not, this can remain a no-op.
        pass
