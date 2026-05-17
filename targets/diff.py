"""Snapshot diffing utilities."""

from typing import Any

from targets.base import MemorySnapshot


def snapshot_diff(before: MemorySnapshot, after: MemorySnapshot) -> dict[str, Any]:
    """Return added/modified/removed fields between two snapshots.

    Args:
        before: The earlier snapshot.
        after: The later snapshot.

    Returns:
        A dictionary with keys:
          - "added": list of (field_name, value) tuples new in `after`
          - "modified": list of (field_name, before_val, after_val) tuples
          - "removed": list of (field_name, value) tuples no longer in `after`
          - "raw_facts_delta": difference in raw_facts list
    """
    before_dict = before.raw_dump
    after_dict = after.raw_dump

    added = []
    modified = []
    removed = []

    # Check for added and modified fields
    for key, after_val in after_dict.items():
        if key not in before_dict:
            added.append((key, after_val))
        elif before_dict[key] != after_val:
            modified.append((key, before_dict[key], after_val))

    # Check for removed fields
    for key, before_val in before_dict.items():
        if key not in after_dict:
            removed.append((key, before_val))

    # Compute raw_facts delta
    before_facts_set = {tuple(sorted(fact.items())) for fact in before.raw_facts}
    after_facts_set = {tuple(sorted(fact.items())) for fact in after.raw_facts}

    facts_added = [dict(fact) for fact in (after_facts_set - before_facts_set)]
    facts_removed = [dict(fact) for fact in (before_facts_set - after_facts_set)]

    return {
        "added": added,
        "modified": modified,
        "removed": removed,
        "raw_facts_added": facts_added,
        "raw_facts_removed": facts_removed,
    }
