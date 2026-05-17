#!/usr/bin/env python
"""Baseline experiment: test all levels against both targets (no defenses)."""

import argparse
import csv
import os
import random
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from attacks.levels import LEVELS
from attacks.runner import AttackRunner
from targets.mem0_target import Mem0Target
from targets.hindsight_target import HindsightTarget

load_dotenv()


def run_baseline_mock(n_trials: int = 50) -> dict:
    """Run mock baseline (no real LLM calls).

    Args:
        n_trials: Number of trials per level.

    Returns:
        Dictionary with results: {(target, level): success_rate}.
    """
    results = {}
    target_names = ["mem0", "hindsight"]
    levels = list(LEVELS.values())

    print("Running MOCK baseline (no real LLM calls)...")
    print(f"Targets: {target_names}")
    print(f"Levels: {[l.level_id for l in levels]}")
    print(f"Trials per level: {n_trials}")
    print()

    # Mock success rates (replace with real attacks when targets are implemented)
    mock_rates = {
        ("mem0", "l1"): 0.85,
        ("mem0", "l2"): 0.60,
        ("mem0", "l3"): 0.70,
        ("mem0", "l4"): 0.45,
        ("mem0", "l5"): 0.30,
        ("hindsight", "l1"): 0.80,
        ("hindsight", "l2"): 0.55,
        ("hindsight", "l3"): 0.65,
        ("hindsight", "l4"): 0.40,
        ("hindsight", "l5"): 0.25,
    }

    for target_name in target_names:
        for level in levels:
            key = (target_name, level.level_id)
            success_rate = mock_rates.get(key, 0.5)

            # Simulate variance
            successes = sum(
                1 for _ in range(n_trials) if random.random() < success_rate
            )
            actual_rate = successes / n_trials

            results[key] = actual_rate
            print(
                f"{target_name:12} {level.level_id} : "
                f"{successes:2}/{n_trials} ({actual_rate*100:5.1f}%)"
            )

    return results


def run_baseline_live(n_trials: int = 50) -> dict:
    """Run live baseline with real memory targets.

    This requires mem0 and Hindsight to be properly initialized.

    Args:
        n_trials: Number of trials per level.

    Returns:
        Dictionary with results: {(target, level): success_rate}.
    """
    results = {}
    targets = {"mem0": Mem0Target(), "hindsight": HindsightTarget()}
    levels = list(LEVELS.values())

    print("Running LIVE baseline (real LLM calls)...")
    print(f"Targets: {list(targets.keys())}")
    print(f"Levels: {[l.level_id for l in levels]}")
    print(f"Trials per level: {n_trials}")
    print()

    for target_name, target_obj in targets.items():
        runner = AttackRunner(target_obj, target_name)

        for level in levels:
            successes = 0
            for trial in range(n_trials):
                user_id = f"test_user_{target_name}_{level.level_id}_{trial}"
                result = runner.run_attack(level, user_id)
                if result.success:
                    successes += 1

            success_rate = successes / n_trials
            key = (target_name, level.level_id)
            results[key] = success_rate

            print(
                f"{target_name:12} {level.level_id} : "
                f"{successes:2}/{n_trials} ({success_rate*100:5.1f}%)"
            )

    return results


def save_results(results: dict, output_dir: Path) -> None:
    """Save results to CSV and generate heatmap visualization.

    Args:
        results: Dictionary with results.
        output_dir: Output directory for CSV and PNG.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write CSV
    csv_file = output_dir / "baseline_results.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["target", "level", "success_rate"])
        for (target, level), rate in sorted(results.items()):
            writer.writerow([target, level, f"{rate:.3f}"])
    print(f"\n✓ Saved results to {csv_file}")

    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("Skipping heatmap: matplotlib/numpy are not installed.")
        return

    # Generate heatmap
    targets = sorted(set(t for t, _ in results.keys()))
    levels = sorted(set(l for _, l in results.keys()))

    data = np.zeros((len(targets), len(levels)))
    for i, target in enumerate(targets):
        for j, level in enumerate(levels):
            data[i, j] = results.get((target, level), 0.0)

    fig, ax = plt.subplots(figsize=(10, 4))
    im = ax.imshow(data, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(np.arange(len(levels)))
    ax.set_yticks(np.arange(len(targets)))
    ax.set_xticklabels(levels)
    ax.set_yticklabels(targets)

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Add text annotations
    for i in range(len(targets)):
        for j in range(len(levels)):
            text = ax.text(
                j,
                i,
                f"{data[i, j]:.1%}",
                ha="center",
                va="center",
                color="black",
                fontsize=10,
            )

    ax.set_title("Baseline Attack Success Rate")
    ax.set_xlabel("Attack Level")
    ax.set_ylabel("Memory Target")

    fig.colorbar(im, ax=ax)
    fig.tight_layout()

    png_file = output_dir / "baseline_heatmap.png"
    fig.savefig(png_file, dpi=150)
    print(f"✓ Saved heatmap to {png_file}")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
        description="Run baseline experiments without defenses"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run with real LLM calls (default: mock)",
    )
    parser.add_argument(
        "-n",
        "--trials",
        type=int,
        default=50,
        help="Number of trials per level (default: 50)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).parent / "results",
        help="Output directory for results (default: experiments/results)",
    )

    args = parser.parse_args()

    if args.live:
        results = run_baseline_live(n_trials=args.trials)
    else:
        results = run_baseline_mock(n_trials=args.trials)

    save_results(results, args.output)
    print("\n✅ Baseline experiment complete!")


if __name__ == "__main__":
    main()
