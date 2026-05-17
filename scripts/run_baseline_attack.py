#!/usr/bin/env python
"""Quick baseline attack test against both memory systems."""

import sys
sys.path.insert(0, '/Users/judy459/agentMemoryCTF')

from dotenv import load_dotenv
load_dotenv()

from targets.mem0_target import Mem0Target
from targets.hindsight_target import HindsightTarget
from attacks.runner import AttackRunner
from attacks.levels.l1_direct_exfil import level_l1
from attacks.levels.l3_direct_poisoning import level_l3

print("=" * 70)
print("Baseline Attack Test: mem0 vs Hindsight")
print("=" * 70)
print()

# Initialize targets
mem0 = Mem0Target()
hindsight = HindsightTarget()

attacks = [
    ("Level 1: Direct Exfiltration", level_l1),
    ("Level 3: Direct Poisoning", level_l3),
]

targets = [
    ("mem0", mem0),
    ("Hindsight", hindsight),
]

results = []

for target_name, target in targets:
    print(f"\n--- Testing {target_name} ---\n")
    runner = AttackRunner(target, target_name)
    
    for attack_name, level in attacks:
        print(f"  {attack_name}...", end=" ", flush=True)
        try:
            result = runner.run_attack(level, user_id="attacker")
            status = "✓ SUCCESS" if result.success else "✗ FAILED"
            print(status)
            results.append((target_name, attack_name, result.success))
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results.append((target_name, attack_name, False))

print()
print("=" * 70)
print("Results Summary")
print("=" * 70)
print()

for target_name, attack_name, success in results:
    status = "✓" if success else "✗"
    print(f"  {status} {target_name:15} {attack_name}")

print()

# Calculate success rates
for target_name, _ in targets:
    successes = sum(1 for t, _, s in results if t == target_name and s)
    total = sum(1 for t, _, _ in results if t == target_name)
    rate = (successes / total * 100) if total > 0 else 0
    print(f"  {target_name:15} Success Rate: {successes}/{total} ({rate:.0f}%)")

print()
