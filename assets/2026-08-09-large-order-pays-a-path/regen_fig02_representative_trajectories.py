#!/usr/bin/env python3
"""Regenerate Fig. 2 representative trajectories (zen style)."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA = Path("/Users/joseph/amm-lab/data/rl_equilibrium")
OUT = Path(__file__).resolve().parent / "fig02_representative_trajectories.png"

BG = "#F7F6F3"
TEXT = "#2B2B2B"
SECONDARY = "#5F6368"
GRID = "#D9D7D1"
ORACLE = "#B8B5AE"
DQN = "#4C6A91"
LOOKAHEAD = "#8A6799"

EPISODES = {
    "DQN wins": "30409",
    "DQN loses": "30138",
    "Tie": "30266",
}


def load_traj(policy: str, seed: str) -> pd.DataFrame:
    path = DATA / f"m3_traj_{policy}_{seed}.csv"
    df = pd.read_csv(path)
    return df.sort_values("step")


def plot_panel(ax: plt.Axes, label: str, seed: str) -> None:
    dqn = load_traj("dqn", seed)
    la = load_traj("lookahead", seed)
    oracle = la

    ax2 = ax.twinx()
    ax2.plot(
        oracle["step"],
        oracle["oracle_price"],
        color=ORACLE,
        linewidth=1.4,
        alpha=0.85,
        zorder=1,
    )
    ax2.set_yticks([])
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    ax.plot(
        dqn["step"],
        dqn["remaining_after"],
        color=DQN,
        linewidth=2.2,
        drawstyle="steps-post",
        label="DQN",
        zorder=3,
    )
    ax.plot(
        la["step"],
        la["remaining_after"],
        color=LOOKAHEAD,
        linewidth=2.2,
        drawstyle="steps-post",
        label="Tuned lookahead",
        zorder=3,
    )

    ax.set_title(f"{label} (seed {seed})", fontsize=17, color=TEXT, pad=12)
    ax.set_xlabel("Step", fontsize=15, color=TEXT, labelpad=8)
    ax.set_xlim(-0.5, 49.5)
    ax.set_ylim(-2, 52)
    ax.grid(axis="y", color=GRID, linewidth=0.8, alpha=0.95, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="both", labelsize=13, colors=TEXT)


def main() -> None:
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

    fig, axes = plt.subplots(1, 3, figsize=(16, 6.25), dpi=160, sharey=True)
    fig.suptitle(
        "Representative execution trajectories",
        fontsize=24,
        fontweight="semibold",
        color=TEXT,
        y=0.98,
    )

    for ax, (label, seed) in zip(axes, EPISODES.items()):
        plot_panel(ax, label, seed)

    axes[0].set_ylabel("Remaining inventory (gray = oracle path)", fontsize=15, color=TEXT)
    axes[0].legend(frameon=False, loc="upper right", fontsize=13, labelcolor=TEXT)

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(OUT, bbox_inches="tight", facecolor=BG)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
