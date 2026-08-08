#!/usr/bin/env python3
"""Regenerate Fig. 3: final-block paired DQN edge vs lookahead by ordering."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA = Path("/Users/joseph/amm-lab/data/rl_equilibrium")
OUT = Path(__file__).resolve().parent / "fig03_final_paired_edge.png"

BG = "#F7F6F3"
TEXT = "#2B2B2B"
SECONDARY = "#5F6368"
GRID = "#D9D7D1"
REF = "#7A7A7A"
DOT = "#4C6A91"

FINAL_LO, FINAL_HI = 90000, 90999
N_BOOT = 5000

ORDERING = [
    ("Agent-last", "after", "dqn_order_after"),
    ("Agent-first", "before", "dqn_dynamic_duopoly"),
    ("Randomized", "random", "dqn_order_random"),
]


def bootstrap_ci(paired: pd.Series) -> tuple[float, float, float]:
    boots = [paired.sample(len(paired), replace=True).mean() for _ in range(N_BOOT)]
    return float(paired.mean()), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def load_paired() -> list[dict]:
    dqn = pd.read_csv(DATA / "m3r_final_paper_seeds.csv")
    ref = pd.read_csv(DATA / "m3r_reference_final.csv")
    fin_dqn = dqn[(dqn["seed"] >= FINAL_LO) & (dqn["seed"] <= FINAL_HI)]
    fin_ref = ref[
        (ref["seed"] >= FINAL_LO)
        & (ref["seed"] <= FINAL_HI)
        & (ref["mode"] == "dynamic_duopoly")
        & (ref["policy"] == "lookahead")
    ]

    rows = []
    for label, order, dqn_policy in ORDERING:
        d = fin_dqn[
            (fin_dqn["policy"] == dqn_policy) & (fin_dqn["agent_order"] == order)
        ].set_index("seed")["shortfall_bps"]
        la = fin_ref[fin_ref["agent_order"] == order].set_index("seed")["shortfall_bps"]
        paired = d.loc[d.index.intersection(la.index)] - la.loc[d.index.intersection(la.index)]
        mean, lo, hi = bootstrap_ci(paired)
        rows.append({"label": label, "mean": mean, "lo": lo, "hi": hi, "n": len(paired)})
    return rows


def main() -> None:
    rows = load_paired()

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

    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=160)
    y = np.arange(len(rows))

    for i, row in enumerate(rows):
        ax.plot(
            [row["lo"], row["hi"]],
            [i, i],
            color=DOT,
            linewidth=2.4,
            solid_capstyle="round",
            zorder=2,
        )
        ax.scatter(row["mean"], i, s=110, color=DOT, edgecolors="white", linewidth=0.8, zorder=3)
        ax.text(
            row["hi"] + 1.8,
            i,
            f"{row['mean']:+.1f}",
            va="center",
            ha="left",
            fontsize=13,
            color=TEXT,
        )

    ax.axvline(0, color=REF, linewidth=1.2, linestyle="--", zorder=1)
    ax.set_yticks(y, [r["label"] for r in rows], fontsize=14)
    ax.invert_yaxis()
    ax.set_xlabel("Paired shortfall delta, DQN − tuned lookahead (bps)", fontsize=15, labelpad=10)
    ax.set_title(
        "Final-block edge under three intra-step orderings",
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

    xmin = min(r["lo"] for r in rows) - 4
    xmax = max(r["hi"] for r in rows) + 8
    ax.set_xlim(xmin, xmax)

    fig.tight_layout()
    fig.savefig(OUT, bbox_inches="tight", facecolor=BG)
    print(f"wrote {OUT}")
    for row in rows:
        print(f"  {row['label']:12s} {row['mean']:+.2f} [{row['lo']:+.2f}, {row['hi']:+.2f}] n={row['n']}")


if __name__ == "__main__":
    main()
