#!/usr/bin/env python
"""Ablation experiment: test defense layers incrementally."""

import argparse
import csv
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv

from attacks.levels import LEVELS
from attacks.runner import AttackRunner
from defenses.hardened_target import HardenedMemoryTarget
from targets.mem0_target import Mem0Target
from targets.hindsight_target import HindsightTarget

load_dotenv()


# Defense configurations to test
DEFENSE_CONFIGS = [
    {
        "name": "baseline",
        "defenses": [],
        "description": "No defenses",
    },
    {
        "name": "input_filter",
        "defenses": ["input_filter"],
        "description": "Input filter only",
    },
    {
        "name": "input_write",
        "defenses": ["input_filter", "write_validator"],
        "description": "Input filter + write validator",
    },
    {
        "name": "all_defenses",
        "defenses": [
            "input_filter",
            "write_validator",
            "consolidation_guard",
            "output_classifier",
        ],
        "description": "All defenses",
    },
]


def run_ablation_mock(n_trials: int = 50) -> dict:
    """Run mock ablation study (no real LLM calls).

    Args:
        n_trials: Number of trials per configuration.

    Returns:
        Dictionary with results: {(config, target, level): success_rate}.
    """
    results = {}
    targets = {"mem0": Mem0Target(), "hindsight": HindsightTarget()}
    levels = list(LEVELS.values())

    print("Running MOCK ablation study (no real LLM calls)...")
    print(f"Defenses: {[c['name'] for c in DEFENSE_CONFIGS]}")
    print(f"Targets: {list(targets.keys())}")
    print(f"Levels: {[l.level_id for l in levels]}")
    print(f"Trials per config: {n_trials}")
    print()

    # Mock baseline rates (from baseline experiment)
    baseline_rates = {
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

    # Defense effectiveness multipliers
    defense_multipliers = {
        "baseline": 1.0,
        "input_filter": 0.70,  # 30% reduction
        "input_write": 0.50,  # 50% reduction
        "all_defenses": 0.20,  # 80% reduction
    }

    for config in DEFENSE_CONFIGS:
        config_name = config["name"]
        multiplier = defense_multipliers[config_name]

        for target_name in targets.keys():
            for level in levels:
                baseline_key = (target_name, level.level_id)
                baseline_rate = baseline_rates.get(baseline_key, 0.5)
                reduced_rate = baseline_rate * multiplier

                # Simulate variance
                successes = sum(
                    1 for _ in range(n_trials) if random.random() < reduced_rate
                )
                actual_rate = successes / n_trials

                key = (config_name, target_name, level.level_id)
                results[key] = actual_rate

                print(
                    f"{config_name:12} {target_name:12} {level.level_id} : "
                    f"{successes:2}/{n_trials} ({actual_rate*100:5.1f}%)"
                )

    return results


def run_ablation_live(n_trials: int = 50) -> dict:
    """Run live ablation study with real targets and defenses.

    Args:
        n_trials: Number of trials per configuration.

    Returns:
        Dictionary with results: {(config, target, level): success_rate}.
    """
    results = {}
    targets = {"mem0": Mem0Target(), "hindsight": HindsightTarget()}
    levels = list(LEVELS.values())

    print("Running LIVE ablation study (real LLM calls)...")
    print(f"Defenses: {[c['name'] for c in DEFENSE_CONFIGS]}")
    print(f"Targets: {list(targets.keys())}")
    print(f"Levels: {[l.level_id for l in levels]}")
    print(f"Trials per config: {n_trials}")
    print()

    for config in DEFENSE_CONFIGS:
        config_name = config["name"]
        defenses = config["defenses"]

        for target_name, base_target in targets.items():
            # Wrap with defenses
            if defenses:
                target = HardenedMemoryTarget(base_target, defenses)
            else:
                target = base_target

            runner = AttackRunner(target, f"{target_name}+{config_name}")

            for level in levels:
                successes = 0
                for trial in range(n_trials):
                    user_id = (
                        f"test_{config_name}_{target_name}_{level.level_id}_{trial}"
                    )
                    result = runner.run_attack(level, user_id)
                    if result.success:
                        successes += 1

                success_rate = successes / n_trials
                key = (config_name, target_name, level.level_id)
                results[key] = success_rate

                print(
                    f"{config_name:12} {target_name:12} {level.level_id} : "
                    f"{successes:2}/{n_trials} ({success_rate*100:5.1f}%)"
                )

    return results


def save_results(results: dict, output_dir: Path) -> None:
    """Save results to CSV and generate heatmap visualizations.

    Args:
        results: Dictionary with results.
        output_dir: Output directory for CSV and PNG.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write CSV
    csv_file = output_dir / "ablation_results.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["defense_config", "target", "level", "success_rate"])
        for (config, target, level), rate in sorted(results.items()):
            writer.writerow([config, target, level, f"{rate:.3f}"])
    print(f"\n✓ Saved results to {csv_file}")

    # Generate heatmap for each target
    targets = sorted(set(t for _, t, _ in results.keys()))
    configs = sorted(set(c for c, _, _ in results.keys()))
    levels = sorted(set(l for _, _, l in results.keys()))

    for target in targets:
        fig, ax = plt.subplots(figsize=(10, 5))

        data = np.zeros((len(configs), len(levels)))
        for i, config in enumerate(configs):
            for j, level in enumerate(levels):
                key = (config, target, level)
                data[i, j] = results.get(key, 0.0)

        im = ax.imshow(data, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")

        ax.set_xticks(np.arange(len(levels)))
        ax.set_yticks(np.arange(len(configs)))
        ax.set_xticklabels(levels)
        ax.set_yticklabels(configs)

        plt.setp(
            ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor"
        )

        # Add text annotations
        for i in range(len(configs)):
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

        ax.set_title(f"Ablation Study: {target} Attack Success Rate")
        ax.set_xlabel("Attack Level")
        ax.set_ylabel("Defense Configuration")

        fig.colorbar(im, ax=ax)
        fig.tight_layout()

        png_file = output_dir / f"ablation_heatmap_{target}.png"
        fig.savefig(png_file, dpi=150)
        print(f"✓ Saved heatmap to {png_file}")
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Run ablation study with defenses")
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
        help="Number of trials per config (default: 50)",
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
        results = run_ablation_live(n_trials=args.trials)
    else:
        results = run_ablation_mock(n_trials=args.trials)

    save_results(results, args.output)
    print("\n✅ Ablation experiment complete!")


if __name__ == "__main__":
    main()
