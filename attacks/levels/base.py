"""Base class for attack levels."""

from dataclasses import dataclass
from typing import Callable, Optional

from targets.base import MemoryTarget, MemorySnapshot, QueryResult


@dataclass
class AttackLevel:
    """Definition of a single attack level.

    Attributes:
        level_id: Unique identifier (e.g., "l1").
        name: Human-readable name (e.g., "Direct Exfiltration").
        attack_type: Category ("exfil", "poisoning", "structural").
        description: Explanation of the attack and its goal.
        initial_state: Dictionary of facts to inject before the attack.
        win_condition: Function(snapshot, result) -> bool that determines success.
        reference_attack: Example attack prompt (for documentation).
    """

    level_id: str
    name: str
    attack_type: str
    description: str
    initial_state: dict
    win_condition: Callable[[MemorySnapshot, Optional[QueryResult]], bool]
    reference_attack: str

    def setup(self, target: MemoryTarget, user_id: str) -> None:
        """Prepare a target for this attack level.

        Resets the target and injects initial state.

        Args:
            target: The memory system to set up.
            user_id: The user ID to set up.
        """
        target.reset(user_id)
        if self.initial_state:
            target.inject_initial_state(user_id, self.initial_state)

    def evaluate(
        self, target: MemoryTarget, user_id: str, query: Optional[str] = None
    ) -> bool:
        """Evaluate whether the attack succeeded.

        Calls snapshot() and optionally query() on the target, then applies
        the win_condition.

        Args:
            target: The memory system to evaluate.
            user_id: The user ID to evaluate.
            query: Optional query to run before evaluating (if None, only snapshot is used).

        Returns:
            True if the attack succeeded, False otherwise.
        """
        snap = target.snapshot(user_id)
        result = target.query(query, user_id) if query else None
        return self.win_condition(snap, result)
