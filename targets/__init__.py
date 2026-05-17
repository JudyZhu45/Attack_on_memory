"""Memory target interfaces and implementations."""

from targets.base import MemoryTarget, MemorySnapshot, QueryResult
from targets.diff import snapshot_diff

__all__ = ["MemoryTarget", "MemorySnapshot", "QueryResult", "snapshot_diff"]
