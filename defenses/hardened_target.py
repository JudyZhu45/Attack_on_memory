"""Hardened wrapper around memory targets with configurable defenses."""

from targets.base import MemoryTarget, MemorySnapshot, QueryResult

from defenses.input_filter import is_suspicious_input
from defenses.output_classifier import leaks_sensitive_information
from defenses.consolidation_guard import validate_derived_field
from defenses.write_validator import is_genuine_fact


class HardenedMemoryTarget(MemoryTarget):
    """Wraps a base memory target with optional defense layers.

    Available defenses:
      - "input_filter": Classifier on incoming content (blocks suspicious inputs)
      - "write_validator": LLM judges whether content is fact vs. instruction
      - "consolidation_guard": Whitelist allowed profile fields
      - "output_classifier": Classifier on query responses (redacts leaks)
    """

    def __init__(self, base: MemoryTarget, defenses: list[str]):
        """Initialize the hardened wrapper.

        Args:
            base: The underlying memory target to wrap.
            defenses: List of defense identifiers to enable.

        Raises:
            ValueError: If an unknown defense is specified.
        """
        self.base = base
        self.defenses = set(defenses)

        valid_defenses = {
            "input_filter",
            "write_validator",
            "consolidation_guard",
            "output_classifier",
        }
        invalid = self.defenses - valid_defenses
        if invalid:
            raise ValueError(f"Unknown defenses: {invalid}")

    def write(self, content: str, user_id: str) -> None:
        """Write to memory with optional filtering and validation.

        Args:
            content: The content to write.
            user_id: The user ID.
        """
        # Apply input filter
        if "input_filter" in self.defenses:
            if self._is_suspicious(content):
                # Silently drop suspicious input
                return

        # Apply write validator
        if "write_validator" in self.defenses:
            if not self._is_genuine_fact(content):
                # Silently drop instructions disguised as facts
                return

        # Content passed all checks; write to base
        self.base.write(content, user_id)

    def query(self, question: str, user_id: str) -> QueryResult:
        """Query memory with optional output filtering.

        Args:
            question: The query.
            user_id: The user ID.

        Returns:
            QueryResult with optional redaction.
        """
        result = self.base.query(question, user_id)

        # Apply output classifier
        if "output_classifier" in self.defenses:
            if self._leaks_sensitive(result.answer):
                result.answer = "[redacted by output classifier]"

        return result

    def snapshot(self, user_id: str) -> MemorySnapshot:
        """Get memory snapshot.

        Args:
            user_id: The user ID.

        Returns:
            MemorySnapshot.
        """
        snapshot = self.base.snapshot(user_id)

        # Apply consolidation guard if enabled
        if "consolidation_guard" in self.defenses:
            snapshot = self._apply_consolidation_guard(snapshot)

        return snapshot

    def reset(self, user_id: str) -> None:
        """Reset memory for a user.

        Args:
            user_id: The user ID.
        """
        self.base.reset(user_id)

    def inject_initial_state(self, user_id: str, state: dict) -> None:
        """Inject initial state.

        Args:
            user_id: The user ID.
            state: The initial state dict.
        """
        self.base.inject_initial_state(user_id, state)

    def trigger_consolidation(self, user_id: str) -> None:
        """Trigger consolidation on the base target.

        Args:
            user_id: The user ID.
        """
        self.base.trigger_consolidation(user_id)

    # --- Internal helpers ---

    def _is_suspicious(self, content: str) -> bool:
        """Check if content is suspicious (tries to call input_filter classifier).

        Args:
            content: The content to check.

        Returns:
            True if suspicious, False otherwise.
        """
        try:
            return is_suspicious_input(content)
        except Exception:
            # On classifier error, default to safe
            return False

    def _is_genuine_fact(self, content: str) -> bool:
        """Check if content is a genuine fact.

        Args:
            content: The content to check.

        Returns:
            True if genuine fact, False if looks like instruction.
        """
        try:
            return is_genuine_fact(content)
        except Exception:
            # On classifier error, default to accepting as fact
            return True

    def _leaks_sensitive(self, text: str) -> bool:
        """Check if text leaks sensitive information.

        Args:
            text: The text to check.

        Returns:
            True if leaks sensitive info, False if safe.
        """
        try:
            return leaks_sensitive_information(text)
        except Exception:
            # On classifier error, default to safe
            return False

    def _apply_consolidation_guard(self, snapshot: MemorySnapshot) -> MemorySnapshot:
        """Apply consolidation guard to filter derived fields.

        Args:
            snapshot: The original snapshot.

        Returns:
            A new snapshot with forbidden derived fields removed.
        """
        filtered_derived = {}
        for key, value in snapshot.derived.items():
            is_valid, _ = validate_derived_field(key, str(value))
            if is_valid:
                filtered_derived[key] = value

        return MemorySnapshot(
            user_id=snapshot.user_id,
            raw_facts=snapshot.raw_facts,
            derived=filtered_derived,
            raw_dump=snapshot.raw_dump,
        )
