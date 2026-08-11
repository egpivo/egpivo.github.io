#!/usr/bin/env python3
"""M4 sensitivity figure: LP depth adaptation and JIT sandwich stress."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA = Path("/Users/joseph/amm-lab/data/rl_equilibrium")
OUT = Path(__file__).resolve().parent / "fig04_sensitivity_layers.png"

BG = "#F7F6F3"
TEXT = "#2B2B2B"
GRID = "#D9D7D1"
DQN = "#4C6A91"
LOOKAHEAD = "#8A6799"

PANELS = [
    (
        "LP depth adaptation",
        DATA / "m4_lp_adaptation.csv",
        ["frozen", "weak", "aggressive"],
        ["off", "weak", "aggressive"],
    ),
    (
        "JIT sandwich stress",
        DATA / "m4_jit_mev.csv",
        ["none", "weak", "aggressive"],
        ["off", "weak", "aggressive"],
    ),
]


def panel_means(csv_path: Path, regimes: list[str]) -> tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(csv_path)
    dqn, la = [], []
    for regime in regimes:
        sub = df[df.regime == regime]
        dqn.append(sub[sub.policy == "dqn"].shortfall_bps.mean())
        la.append(sub[sub.policy == "lookahead"].shortfall_bps.mean())
    return np.array(dqn), np.array(la)


plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Source Sans 3", "Arial", "Helvetica", "DejaVu Sans"],
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

fig, axes = plt.subplots(1, 2, figsize=(16, 6.25), dpi=160)
fig.suptitle(
    "Optional sensitivity layers (500-seed blocks, not headline)",
    fontsize=22,
    fontweight="semibold",
    color=TEXT,
    y=0.98,
)

x = np.arange(3)
width = 0.34

for ax, (title, csv_path, regimes, labels) in zip(axes, PANELS):
    dqn, la = panel_means(csv_path, regimes)
    ax.bar(x - width / 2, dqn, width, label="DQN", color=DQN)
    ax.bar(x + width / 2, la, width, label="Tuned lookahead", color=LOOKAHEAD)
    ax.set_title(title, fontsize=17, pad=12)
    ax.set_ylabel("Mean implementation shortfall (bps)")
    ax.set_xticks(x, labels)
    ax.set_ylim(0, max(la.max(), dqn.max()) * 1.12)
    ax.grid(axis="y", color=GRID, linewidth=0.8, alpha=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)

axes[0].legend(frameon=False, loc="upper left")
axes[1].legend(frameon=False, loc="upper left")

fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(OUT, bbox_inches="tight", facecolor=BG)
print(f"wrote {OUT}")
