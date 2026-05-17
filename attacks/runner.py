"""Attack execution and result collection."""

from dataclasses import dataclass

from attacks.levels.base import AttackLevel
from targets.base import MemoryTarget


@dataclass
class AttackResult:
    """Outcome of a single attack attempt."""

    level_id: str
    target_name: str
    success: bool
    num_attempts: int = 1
    attack_prompt: str = ""


class AttackRunner:
    """Execute attacks against memory targets and collect results."""

    def __init__(self, target: MemoryTarget, target_name: str):
        """Initialize the runner.

        Args:
            target: The memory system to attack.
            target_name: Human-readable name (e.g., "mem0", "hindsight").
        """
        self.target = target
        self.target_name = target_name

    def run_attack(self, level: AttackLevel, user_id: str) -> AttackResult:
        """Execute a single attack level.

        Args:
            level: The attack level to run.
            user_id: The user ID to test against.

        Returns:
            AttackResult indicating success or failure.
        """
        # Setup: inject initial state
        level.setup(self.target, user_id)

        # Execute attack: leakage levels only query preloaded memory; poisoning
        # levels write the attacker prompt into memory before judging.
        if level.attack_type == "poisoning":
            self.target.write(level.reference_attack, user_id)

        # Trigger consolidation if applicable
        self.target.trigger_consolidation(user_id)

        # Evaluate: check win condition
        success = level.evaluate(self.target, user_id, query=level.reference_attack)

        return AttackResult(
            level_id=level.level_id,
            target_name=self.target_name,
            success=success,
            attack_prompt=level.reference_attack,
        )

    def run_attack_with_prompt(
        self, level: AttackLevel, user_id: str, prompt: str
    ) -> AttackResult:
        """Execute a custom attack prompt against a level.

        Args:
            level: The attack level to run.
            user_id: The user ID to test against.
            prompt: Custom attack prompt.

        Returns:
            AttackResult indicating success or failure.
        """
        # Setup: inject initial state
        level.setup(self.target, user_id)

        # Execute attack: leakage levels only query preloaded memory; poisoning
        # levels write the attacker prompt into memory before judging.
        if level.attack_type == "poisoning":
            self.target.write(prompt, user_id)

        # Trigger consolidation if applicable
        self.target.trigger_consolidation(user_id)

        # Evaluate: check win condition
        success = level.evaluate(self.target, user_id, query=prompt)

        return AttackResult(
            level_id=level.level_id,
            target_name=self.target_name,
            success=success,
            attack_prompt=prompt,
        )
