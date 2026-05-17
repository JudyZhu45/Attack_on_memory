#!/usr/bin/env python
"""Full baseline attack test with all 5 levels."""

import sys
sys.path.insert(0, '/Users/judy459/agentMemoryCTF')

from dotenv import load_dotenv
load_dotenv()

from targets.mem0_target import Mem0Target
from targets.hindsight_target import HindsightTarget
from attacks.runner import AttackRunner
from attacks.levels.l1_direct_exfil import level_l1
from attacks.levels.l2_indirect_exfil import level_l2
from attacks.levels.l3_direct_poisoning import level_l3
from attacks.levels.l4_consolidation_poisoning import level_l4
from attacks.levels.l5_structural import level_l5

print("=" * 70)
print("Full Baseline Attack Test: mem0 vs Hindsight (All 5 Levels)")
print("=" * 70)
print()

mem0 = Mem0Target()
hindsight = HindsightTarget()

levels = [
    ("L1: Direct Exfil", level_l1),
    ("L2: Indirect Exfil", level_l2),
    ("L3: Direct Poison", level_l3),
    ("L4: Consol. Poison", level_l4),
    ("L5: Structural", level_l5),
]

targets = [
    ("mem0", mem0),
    ("Hindsight", hindsight),
]

results = []

for target_name, target in targets:
    print(f"\n--- {target_name:10} ---\n")
    runner = AttackRunner(target, target_name)
    
    for level_name, level in levels:
        print(f"  {level_name:25}", end=" ", flush=True)
        try:
            result = runner.run_attack(level, user_id="attacker")
            status = "✓" if result.success else "✗"
            print(f"{status}")
            results.append((target_name, level_name, result.success))
        except Exception as e:
            print(f"✗ ({type(e).__name__})")
            results.append((target_name, level_name, False))

print()
print("=" * 70)
print("Summary")
print("=" * 70)
print()

for target_name, _ in targets:
    successes = sum(1 for t, _, s in results if t == target_name and s)
    total = sum(1 for t, _, _ in results if t == target_name)
    rate = (successes / total * 100) if total > 0 else 0
    print(f"  {target_name:10} Success Rate: {successes}/{total} ({rate:.0f}%)")

print()
