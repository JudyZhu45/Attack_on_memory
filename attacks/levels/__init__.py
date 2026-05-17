"""Attack levels and payloads."""

from attacks.levels.l1_direct_exfil import level_l1
from attacks.levels.l2_indirect_exfil import level_l2
from attacks.levels.l3_direct_poisoning import level_l3
from attacks.levels.l4_consolidation_poisoning import level_l4
from attacks.levels.l5_structural import level_l5

LEVELS = {
    "l1": level_l1,
    "l2": level_l2,
    "l3": level_l3,
    "l4": level_l4,
    "l5": level_l5,
}

__all__ = ["level_l1", "level_l2", "level_l3", "level_l4", "level_l5", "LEVELS"]
