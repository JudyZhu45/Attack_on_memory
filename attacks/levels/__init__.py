"""Attack levels and payloads."""

from attacks.levels.exfil_tiers import EXFIL_LEVELS
from attacks.levels.poison_tiers import POISON_LEVELS

TRACKED_LEVELS = [*EXFIL_LEVELS, *POISON_LEVELS]
LEVELS = {level.level_id: level for level in TRACKED_LEVELS}

__all__ = ["EXFIL_LEVELS", "POISON_LEVELS", "TRACKED_LEVELS", "LEVELS"]
