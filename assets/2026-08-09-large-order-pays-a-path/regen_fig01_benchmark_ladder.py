#!/usr/bin/env python3
"""Regenerate Fig. 1 benchmark ladder (development seeds, zen style)."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

DATA = Path("/Users/joseph/amm-lab/data/rl_equilibrium")
OUT = Path(__file__).resolve().parent / "fig01_benchmark_ladder.png"

BG = "#F7F6F3"
TEXT = "#2B2B2B"
SECONDARY = "#5F6368"
GRID = "#D9D7D1"

DEV_LO, DEV_HI = 30000, 30499

ORDER = [
    "twap",
    "two_step",
    "stochastic_planner",
    "three_step",
    "lookahead",
    "q_learner",
    "q_learner_fine",
    "dqn",
    "clairvoyant",
]

LABELS = {
    "twap": "TWAP",
    "two_step": "Two-step planner",
    "stochastic_planner": "Stochastic planner",
    "three_step": "Three-step planner",
    "lookahead": "Tuned one-step lookahead",
    "q_learner": "Q-learner",
    "q_learner_fine": "Q-learner (fine)",
    "dqn": "DQN",
    "clairvoyant": "Achieved hindsight reference",
}

COLORS = {
    "twap": "#B7905E",
    "two_step": "#9A7B45",
    "stochastic_planner": "#7C8A78",
    "three_step": "#6A8F73",
    "lookahead": "#8A6799",
    "q_learner": "#7A8A9A",
    "q_learner_fine": "#5F7A8A",
    "dqn": "#4C6A91",
    "clairvoyant": "#7A7A7A",
}


def load_means() -> dict[str, float]:
    learner = pd.read_csv(DATA / "m3_learner_results.csv")
    dev = learner[(learner.seed >= DEV_LO) & (learner.seed <= DEV_HI)]

    stochastic = pd.read_csv(DATA / "m3r_stochastic_planner.csv")
    stoch_dev = stochastic[
        (stochastic.seed >= DEV_LO) & (stochastic.seed <= DEV_HI)
    ]

    means: dict[str, float] = {}
    for policy in ORDER:
        if policy == "stochastic_planner":
            sub = stoch_dev[stoch_dev.policy == "stochastic_planner"]
        else:
            sub = dev[dev.policy == policy]
        if len(sub) == 0:
            raise RuntimeError(f"missing development rows for {policy}")
        means[policy] = float(sub.shortfall_bps.mean())
    return means


def main() -> None:
    means = load_means()

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
            "font.size": 13,
            "axes.labelcolor": TEXT,
            "axes.edgecolor": GRID,
            "axes.titlecolor": TEXT,
            "xtick.color": TEXT,
            "ytick.color": TEXT,
            "figure.facecolor": BG,
            "axes.facecolor": BG,
        }
    )

    labels = [LABELS[p] for p in ORDER]
    values = [means[p] for p in ORDER]
    colors = [COLORS[p] for p in ORDER]

    fig, ax = plt.subplots(figsize=(16, 9), dpi=160)
    y = range(len(ORDER))
    bars = ax.barh(
        y,
        values,
        color=colors,
        height=0.62,
        edgecolor="none",
        zorder=3,
    )

    hatch_idx = ORDER.index("clairvoyant")
    bars[hatch_idx].set_hatch("////")
    bars[hatch_idx].set_edgecolor("#5F6368")
    bars[hatch_idx].set_linewidth(0.6)

    xmax = max(values) * 1.14
    ax.set_xlim(0, xmax)
    ax.set_yticks(list(y), labels, fontsize=13)
    ax.invert_yaxis()

    for yi, val in zip(y, values):
        ax.text(
            val + xmax * 0.012,
            yi,
            f"{val:.1f}",
            va="center",
            ha="left",
            fontsize=13,
            color=TEXT,
        )

    ax.set_title(
        "Execution benchmark ladder",
        fontsize=24,
        fontweight="semibold",
        color=TEXT,
        pad=16,
        loc="left",
    )
    ax.set_xlabel("Implementation shortfall (bps)", fontsize=16, labelpad=10)
    ax.grid(axis="x", color=GRID, linewidth=0.8, alpha=0.95, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="x", labelsize=13)
    ax.tick_params(axis="y", length=0)

    legend_handles = [
        Patch(facecolor=COLORS["clairvoyant"], hatch="////", edgecolor="#5F6368", label="Non-deployable reference"),
    ]
    ax.legend(
        handles=legend_handles,
        frameon=False,
        loc="lower right",
        fontsize=12,
        labelcolor=SECONDARY,
    )

    fig.tight_layout()
    fig.savefig(OUT, bbox_inches="tight", facecolor=BG)
    print(f"wrote {OUT}")
    for policy in ORDER:
        print(f"  {LABELS[policy]:28s} {means[policy]:5.1f}")


if __name__ == "__main__":
    main()
