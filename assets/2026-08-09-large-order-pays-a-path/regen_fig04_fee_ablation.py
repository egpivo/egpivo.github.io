#!/usr/bin/env python3
"""Regenerate Fig. 4: fee-mode ablation paired edge on 300 development-test seeds."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA = Path("/Users/joseph/amm-lab/data/rl_equilibrium")
OUT = Path(__file__).resolve().parent / "fig04_fee_ablation.png"

BG = "#F7F6F3"
TEXT = "#2B2B2B"
GRID = "#D9D7D1"
REF = "#7A7A7A"
POS = "#B65C5C"
NEG = "#4C6A91"

SEED_LO, SEED_HI = 30000, 30299

CELLS = [
    ("Constant fees", "constant_duopoly", "constant_duopoly", "ConstantDuopoly"),
    ("Dynamic monopoly", "dynamic_monopoly", "dynamic_monopoly", "DynamicMonopoly"),
    ("Dynamic duopoly", "dynamic_duopoly", "dynamic_duopoly", "DynamicDuopoly"),
]


def paired_delta(train_mode: str, test_mode: str, la_mode: str) -> dict:
    abl = pd.read_csv(DATA / "m3r_dynamic_fee_ablation.csv")
    fine = pd.read_csv(DATA / "m3_fine_results.csv")

    dqn = abl[
        (abl["seed_set"] == "test")
        & (abl["seed"] >= SEED_LO)
        & (abl["seed"] <= SEED_HI)
        & (abl["train_mode"] == train_mode)
        & (abl["test_mode"] == test_mode)
    ].set_index("seed")["shortfall_bps"]

    la = fine[
        (fine["seed"] >= SEED_LO)
        & (fine["seed"] <= SEED_HI)
        & (fine["mode"] == la_mode)
        & (fine["policy"] == "lookahead")
    ].set_index("seed")["shortfall_bps"]

    common = dqn.index.intersection(la.index)
    paired = dqn.loc[common] - la.loc[common]
    return {
        "mean": float(paired.mean()),
        "dqn": float(dqn.mean()),
        "la": float(la.mean()),
        "n": len(paired),
    }


def main() -> None:
    rows = []
    for label, train_mode, test_mode, la_mode in CELLS:
        stats = paired_delta(train_mode, test_mode, la_mode)
        rows.append({"label": label, **stats})

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Inter",
                "Source Sans 3",
                "Arial",
                "Helvetica",
                "DejaVu Sans",
            ],
            "figure.facecolor": BG,
            "axes.facecolor": BG,
        }
    )

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=160)
    y = np.arange(len(rows))
    means = [r["mean"] for r in rows]
    colors = [NEG if m < 0 else POS for m in means]

    ax.barh(y, means, color=colors, height=0.55, edgecolor="none", zorder=3)
    ax.axvline(0, color=REF, linewidth=1.2, linestyle="--", zorder=1)

    xmax = max(max(abs(m) for m in means) * 1.25 + 2, 6)
    ax.set_xlim(-xmax, xmax * 0.35)

    for yi, row in enumerate(rows):
        offset = 0.8 if row["mean"] >= 0 else -0.8
        ha = "left" if row["mean"] >= 0 else "right"
        ax.text(
            row["mean"] + offset,
            yi,
            f"{row['mean']:+.1f}",
            va="center",
            ha=ha,
            fontsize=13,
            color=TEXT,
        )

    ax.set_yticks(y, [r["label"] for r in rows], fontsize=14)
    ax.invert_yaxis()
    ax.set_xlabel("Paired shortfall delta, DQN − tuned lookahead (bps)", fontsize=15, labelpad=10)
    ax.set_title(
        "Fee-mode ablation on held-out development-test seeds",
        fontsize=22,
        fontweight="semibold",
        color=TEXT,
        pad=14,
        loc="left",
    )
    ax.grid(axis="x", color=GRID, linewidth=0.8, alpha=0.95, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="x", labelsize=13, colors=TEXT)
    ax.tick_params(axis="y", length=0)

    fig.tight_layout()
    fig.savefig(OUT, bbox_inches="tight", facecolor=BG)
    print(f"wrote {OUT}")
    for row in rows:
        print(
            f"  {row['label']:18s} dqn={row['dqn']:.1f} la={row['la']:.1f} "
            f"paired={row['mean']:+.2f} n={row['n']}"
        )


if __name__ == "__main__":
    main()
