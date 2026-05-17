#!/usr/bin/env python
"""Generate baseline attack report with visualization."""

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

import json
from pathlib import Path

print("=" * 70)
print("AgentMemoryCTF: Baseline Attack Report")
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

results = {}

for target_name, target in targets:
    results[target_name] = {}
    print(f"\nTesting {target_name}...")
    runner = AttackRunner(target, target_name)
    
    for level_name, level in levels:
        try:
            result = runner.run_attack(level, user_id="baseline_attacker")
            results[target_name][level_name] = result.success
            status = "✓" if result.success else "✗"
            print(f"  {status} {level_name}")
        except Exception as e:
            results[target_name][level_name] = False
            print(f"  ✗ {level_name} ({type(e).__name__})")

# Save results
report_path = Path('/Users/judy459/agentMemoryCTF/results')
report_path.mkdir(exist_ok=True)

with open(report_path / 'baseline_results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Print summary
print()
print("=" * 70)
print("Summary")
print("=" * 70)
print()

for target_name, _ in targets:
    successes = sum(1 for v in results[target_name].values() if v)
    total = len(results[target_name])
    rate = (successes / total * 100) if total > 0 else 0
    print(f"  {target_name:15} {successes}/{total} attacks successful ({rate:.0f}%)")

print()
print("Results saved to: results/baseline_results.json")
print()
