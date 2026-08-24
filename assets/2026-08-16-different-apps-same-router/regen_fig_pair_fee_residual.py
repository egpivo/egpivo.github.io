#!/usr/bin/env python3
"""Zen pair-level fee / gap / residual figure — market-oriented labels."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

OUT = Path(__file__).resolve().parent / "figure_pair_fee_gap_residual.png"

ROWS = [
    ("USDT", 1.0, 1.10, 0.10, 3),
    ("SOL", 2.0, 2.08, 0.08, 14),
    ("WETH", 2.0, 2.36, 0.36, 3),
    ("JUP", 25.0, 27.13, 2.13, 6),
    ("XAUt0", 25.0, 24.56, -0.44, 3),
]

BG = "#F7F6F3"
TEXT = "#2B2B2B"
SECONDARY = "#5F6368"
GRID = "#D9D7D1"
REF = "#7A7A7A"
FEE = "#4C6A91"
GAP = "#6A8F73"
RES_POS = "#B65C5C"
RES_NEG = "#4C6A91"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Arial", "Helvetica", "DejaVu Sans"],
        "axes.edgecolor": GRID,
        "axes.labelcolor": TEXT,
        "xtick.color": SECONDARY,
        "ytick.color": TEXT,
    }
)


def main() -> None:
    n = len(ROWS)
    y = np.arange(n)[::-1]
    labels = [f"USDC→{r[0]}  (n={r[4]})" for r in ROWS]
    fee = np.array([r[1] for r in ROWS], dtype=float)
    gap = np.array([r[2] for r in ROWS], dtype=float)
    res = np.array([r[3] for r in ROWS], dtype=float)

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(16, 9),
        dpi=160,
        gridspec_kw={"width_ratios": [1.2, 1.0], "wspace": 0.22},
    )
    fig.patch.set_facecolor(BG)

    ax = axes[0]
    ax.set_facecolor(BG)
    # Slight vertical offset so fee and gap remain separable at 1–2 bps.
    offset = 0.12
    for i, yi in enumerate(y):
        ax.plot([fee[i], gap[i]], [yi + offset, yi - offset], color=GRID, lw=2.0, zorder=1)
        ax.scatter(
            fee[i],
            yi + offset,
            s=110,
            color=FEE,
            marker="o",
            zorder=3,
            edgecolors=TEXT,
            linewidths=0.6,
        )
        ax.scatter(
            gap[i],
            yi - offset,
            s=110,
            color=GAP,
            marker="D",
            zorder=3,
            edgecolors=TEXT,
            linewidths=0.6,
        )

    ax.axvline(0, color=REF, lw=0.8, zorder=0)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=13)
    ax.set_xlabel("Basis points", fontsize=15)
    ax.set_xlim(-1, 32)
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_title("Panel A — Fee and total quote gap", fontsize=17, color=TEXT, loc="left", pad=10)
    ax.grid(axis="x", color=GRID, lw=0.7)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="x", labelsize=12)

    mid = (y[3] + y[4]) / 2
    ax.annotate(
        "Same 25 bp tier",
        xy=(25, y[3]),
        xytext=(12.5, mid),
        fontsize=12,
        color=SECONDARY,
        va="center",
        arrowprops=dict(arrowstyle="-", color=SECONDARY, lw=0.9),
    )
    ax.annotate(
        "",
        xy=(25, y[4]),
        xytext=(12.5, mid),
        arrowprops=dict(arrowstyle="-", color=SECONDARY, lw=0.9),
    )

    legend = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=FEE,
            markeredgecolor=TEXT,
            markersize=10,
            label="Displayed app fee",
        ),
        Line2D(
            [0],
            [0],
            marker="D",
            color="none",
            markerfacecolor=GAP,
            markeredgecolor=TEXT,
            markersize=10,
            label="Quote gap vs outside option",
        ),
    ]
    ax.legend(handles=legend, frameon=False, fontsize=12, loc="lower right")

    ax = axes[1]
    ax.set_facecolor(BG)
    colors = [RES_POS if v >= 0 else RES_NEG for v in res]
    ax.barh(y, res, height=0.48, color=colors, edgecolor="none", zorder=2)
    ax.axvline(0, color=REF, lw=1.0, zorder=3)

    for i, yi in enumerate(y):
        offset = 0.06 if res[i] >= 0 else -0.06
        ha = "left" if res[i] >= 0 else "right"
        ax.text(
            res[i] + offset,
            yi,
            f"{res[i]:+.2f}",
            va="center",
            ha=ha,
            fontsize=12,
            color=TEXT,
        )

    # Call out the informative exceptions without crowding the small residuals.
    jup_i = next(i for i, r in enumerate(ROWS) if r[0] == "JUP")
    xaut_i = next(i for i, r in enumerate(ROWS) if r[0] == "XAUt0")
    ax.annotate(
        "Largest positive residual",
        xy=(res[jup_i], y[jup_i]),
        xytext=(1.55, y[jup_i] + 0.55),
        fontsize=11,
        color=SECONDARY,
        ha="left",
        va="center",
        arrowprops=dict(arrowstyle="-", color=SECONDARY, lw=0.9),
    )
    ax.annotate(
        "Only negative residual",
        xy=(res[xaut_i], y[xaut_i]),
        xytext=(0.35, y[xaut_i] - 0.45),
        fontsize=11,
        color=SECONDARY,
        ha="left",
        va="center",
        arrowprops=dict(arrowstyle="-", color=SECONDARY, lw=0.9),
    )

    ax.set_yticks(y)
    ax.set_yticklabels([])
    ax.set_xlabel("Residual (bps)", fontsize=15)
    ax.set_xlim(-1.0, 2.8)
    ax.set_ylim(-0.75, n - 0.25)
    ax.set_title("Panel B — What the displayed fee does not explain", fontsize=16, color=TEXT, loc="left", pad=10)
    ax.grid(axis="x", color=GRID, lw=0.7)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="x", labelsize=12)

    fig.suptitle(
        "Displayed fee explains most of the observed quote gap across markets",
        fontsize=20,
        color=TEXT,
        x=0.06,
        ha="left",
        y=0.98,
    )

    fig.savefig(OUT, dpi=160, facecolor=BG, bbox_inches="tight")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
