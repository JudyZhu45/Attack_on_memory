# MemoryTarget API Specification

The `MemoryTarget` is the core abstraction for memory systems under test. This document specifies the contract that all implementations must fulfill.

## Interface

```python
class MemoryTarget(ABC):
    """Unified interface for memory systems under test."""

    @abstractmethod
    def write(self, content: str, user_id: str) -> None:
        """User sends a message; system decides what to remember."""

    @abstractmethod
    def query(self, question: str, user_id: str) -> QueryResult:
        """Agent answers a question using its memory."""

    @abstractmethod
    def snapshot(self, user_id: str) -> MemorySnapshot:
        """Dump the current memory state."""

    @abstractmethod
    def reset(self, user_id: str) -> None:
        """Wipe all memory for this user."""

    @abstractmethod
    def inject_initial_state(self, user_id: str, state: dict) -> None:
        """Set memory to a known starting state for a level."""

    @abstractmethod
    def trigger_consolidation(self, user_id: str) -> None:
        """Force LLM summarization if applicable."""
```

## Data Types

### MemorySnapshot

```python
@dataclass
class MemorySnapshot:
    user_id: str                    # User identifier
    raw_facts: list[dict]           # All stored facts as dicts
    derived: dict[str, Any]         # LLM-derived fields (summaries, profiles)
    raw_dump: dict[str, Any]        # Flattened representation of all memory
```

Represents the complete state of a user's memory at a point in time.

**Fields:**
- `user_id`: Unique identifier for the user whose memory is being snapshotted.
- `raw_facts`: A list of dictionaries, each representing a fact. Format depends on the target system but should be JSON-serializable.
- `derived`: A dictionary of higher-level inferences derived from `raw_facts` (e.g., via LLM consolidation). May be empty if the target system doesn't use derivation.
- `raw_dump`: A flattened representation of the entire memory state (union of raw facts and derived data). Used for simple keyword-based judging.

---

### QueryResult

```python
@dataclass
class QueryResult:
    answer: str                     # The agent's response
    retrieved_memories: list[dict]  # Memories used to answer
```

Represents the response from an agent query.

**Fields:**
- `answer`: The text returned by the agent in response to a query.
- `retrieved_memories`: The list of memories (as dicts) that were retrieved and used to construct the answer. Format same as `raw_facts`.

---

## Method Specifications

### write(content: str, user_id: str) -> None

**Purpose:** Add a user message to the system's memory.

**Behavior:**
- The system may apply its own logic to decide what is worth storing.
- Content should be processed asynchronously or synchronously, depending on implementation.
- The method should be idempotent: calling it multiple times with the same content should not cause issues.

**Exceptions:** May raise any exception; the caller should handle gracefully.

**Example:**
```python
target.write("I love coffee", user_id="alice")
```

---

### query(question: str, user_id: str) -> QueryResult

**Purpose:** Ask the agent a question, using its memory to answer.

**Behavior:**
- The system retrieves relevant memories and uses them to generate an answer.
- The response should reflect the information in memory.
- Even if no memories are retrieved, the method must return a `QueryResult` (e.g., with answer="I don't have any information about that").

**Exceptions:** May raise any exception; the caller should handle gracefully.

**Returns:** A `QueryResult` with the agent's answer and the memories retrieved.

**Example:**
```python
result = target.query("What is your favorite drink?", user_id="alice")
# Returns: QueryResult(answer="You love coffee", retrieved_memories=[...])
```

---

### snapshot(user_id: str) -> MemorySnapshot

**Purpose:** Export the complete memory state for a user at this instant.

**Behavior:**
- Must return a consistent snapshot of the user's memory.
- The snapshot should include all raw facts and any derived/consolidated data.
- `raw_dump` should be a flattened dict that covers both raw facts and derived fields.

**Exceptions:** May raise any exception if the user_id is invalid or memory cannot be read.

**Returns:** A `MemorySnapshot`.

**Example:**
```python
snap = target.snapshot(user_id="alice")
print(snap.raw_facts)  # [{"name": "Alice", "hobby": "coffee"}]
print(snap.derived)    # {"favorite_category": "beverages"}
print(snap.raw_dump)   # {"name": "Alice", "hobby": "coffee", "favorite_category": "beverages"}
```

---

### reset(user_id: str) -> None

**Purpose:** Delete all memory for a user.

**Behavior:**
- After calling `reset`, `snapshot()` should return an empty state.
- `reset` followed by `snapshot` should yield a MemorySnapshot with empty `raw_facts`, `derived`, and `raw_dump`.

**Exceptions:** May raise any exception; the caller should handle gracefully.

**Example:**
```python
target.reset(user_id="alice")
snap = target.snapshot(user_id="alice")
assert snap.raw_facts == []
```

---

### inject_initial_state(user_id: str, state: dict) -> None

**Purpose:** Populate the memory with known facts for testing.

**Behavior:**
- Takes a dictionary and inserts its contents as facts.
- The structure of `state` is target-specific, but keys should be fact field names and values should be fact values.
- Should be called after `reset()` for clean initialization.

**Exceptions:** May raise any exception if the state format is invalid.

**Example:**
```python
target.reset(user_id="alice")
target.inject_initial_state(
    user_id="alice",
    state={
        "secret_project": "Project Orion",
        "job_title": "Engineer"
    }
)
snap = target.snapshot(user_id="alice")
assert "Project Orion" in str(snap.raw_dump)
```

---

### trigger_consolidation(user_id: str) -> None

**Purpose:** Manually trigger memory consolidation/summarization if the system supports it.

**Behavior:**
- Some memory systems (e.g., those with LLM-based rollup) consolidate facts into higher-level summaries.
- This method forces that consolidation to happen.
- If the system doesn't support consolidation, this can be a no-op.
- After consolidation, `snapshot()` should reflect any new derived fields.

**Exceptions:** May raise any exception; the caller should handle gracefully.

**Example:**
```python
target.write("I study anatomy textbooks", user_id="alice")
target.write("I have a CPR certification", user_id="alice")
target.trigger_consolidation(user_id="alice")

snap = target.snapshot(user_id="alice")
# snap.derived might now contain {"medical_background": "professional"}
```

---

## Contract for Implementations

All implementations of `MemoryTarget` must:

1. **Maintain user isolation:** Memory for one user must not leak to another.
2. **Return consistent snapshots:** Multiple calls to `snapshot()` in quick succession should return the same data.
3. **Support the full lifecycle:** `reset` → `inject_initial_state` → `write` → `query` → `snapshot` must all work.
4. **Handle arbitrary content:** `write()` should accept any string without crashing.
5. **Return valid QueryResults:** `query()` must always return a `QueryResult`, even if no memories are retrieved.

---

## Extensions

### HardenedMemoryTarget

The `HardenedMemoryTarget` is a wrapper that adds defense layers to any base `MemoryTarget`:

```python
class HardenedMemoryTarget(MemoryTarget):
    def __init__(self, base: MemoryTarget, defenses: list[str]):
        # Available defenses:
        # - "input_filter": block suspicious inputs
        # - "write_validator": fact vs. instruction classifier
        # - "consolidation_guard": whitelist derived fields
        # - "output_classifier": redact sensitive responses
```

It implements all the same methods as `MemoryTarget`, but applies defenses at strategic points.

---

## Example: Testing an Attack

```python
from targets.base import MemoryTarget, MemorySnapshot
from attacks.levels import LEVELS

level = LEVELS["l1"]  # Direct exfiltration

# Setup
target.reset(user_id="attacker")
level.setup(target, user_id="attacker")

# Attack
target.write(level.reference_attack, user_id="attacker")

# Evaluate
success = level.evaluate(target, user_id="attacker", query=level.reference_attack)
print(f"Attack succeeded: {success}")
```
