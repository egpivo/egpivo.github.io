#!/usr/bin/env python3
"""DFlow-centered emerging Solana trading stack hero — zen, non-promotional."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).resolve().parent / "hero.png"

BG = "#F7F6F3"
TEXT = "#2B2B2B"
SECONDARY = "#5F6368"
GRID = "#D9D7D1"
DIST = "#4C6A91"      # distribution
EXEC = "#6A8F73"      # wholesale execution (DFlow)
LIQ = "#8A6799"       # liquidity
AUTH = "#B7905E"      # authorization / delivery / settlement
HL_BG = "#E8E4DC"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Arial", "Helvetica", "DejaVu Sans"],
    }
)


def box(ax, x, y, w, h, facecolor, title, lines, title_size=13):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.2,
        edgecolor=TEXT,
        facecolor=facecolor,
        mutation_aspect=0.3,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="top", fontsize=title_size, color=TEXT, fontweight="bold")
    for i, line in enumerate(lines):
        ax.text(x + w / 2, y + h - 0.62 - i * 0.32, line, ha="center", va="top", fontsize=11, color=SECONDARY)


def arrow(ax, x, y0, y1):
    ax.annotate(
        "",
        xy=(x, y1),
        xytext=(x, y0),
        arrowprops=dict(arrowstyle="-|>", color=SECONDARY, lw=1.4, mutation_scale=12),
    )


def main() -> None:
    fig, ax = plt.subplots(figsize=(16, 10), dpi=160)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis("off")

    ax.text(0.3, 11.5, "The Emerging Solana Trading Stack", fontsize=24, color=TEXT, ha="left", va="top")

    # Highlight labels (left)
    ax.add_patch(
        FancyBboxPatch((0.25, 8.55), 2.2, 0.7, boxstyle="round,pad=0.02,rounding_size=0.06",
                       facecolor=HL_BG, edgecolor=DIST, lw=1.2)
    )
    ax.text(1.35, 8.9, "Retail pricing\ndiscretion", ha="center", va="center", fontsize=11, color=DIST)

    ax.add_patch(
        FancyBboxPatch((0.25, 6.35), 2.2, 0.7, boxstyle="round,pad=0.02,rounding_size=0.06",
                       facecolor=HL_BG, edgecolor=EXEC, lw=1.2)
    )
    ax.text(1.35, 6.7, "Wholesale\nexecution", ha="center", va="center", fontsize=11, color=EXEC)

    cx = 5.5
    w = 5.2

    # Layer boxes top to bottom
    box(ax, cx - w / 2, 9.35, w, 1.35, "#D9E2EC",
        "App / Wallet / Agent",
        ["retail quote + app fee", "distribution · customer acquisition"])
    arrow(ax, cx, 9.35, 8.55)

    box(ax, cx - w / 2, 6.55, w, 1.7, "#DCE8DE",
        "DFlow",
        ["liquidity search · route selection", "transaction construction · execution policy",
         "representative wholesale execution layer"])
    arrow(ax, cx, 6.55, 5.75)

    box(ax, cx - w / 2, 4.55, w, 1.15, "#E6DCEC",
        "AMMs · CLOBs · Market Makers",
        ["liquidity production · specialized venues"])
    arrow(ax, cx, 4.55, 3.85)

    box(ax, cx - w / 2, 2.85, w, 0.95, "#F0E6D8",
        "Wallet Authorization",
        ["user or agent signature"])
    arrow(ax, cx, 2.85, 2.25)

    box(ax, cx - w / 2, 1.45, w, 0.75, "#F0E6D8",
        "Delivery",
        ["RPC / block-engine path"], title_size=12)
    arrow(ax, cx, 1.45, 0.95)

    box(ax, cx - w / 2, 0.15, w, 0.75, "#F0E6D8",
        "Solana Execution and Settlement",
        ["program execution · final settlement"], title_size=12)

    ax.text(
        0.3,
        0.05,
        "Functional framework — not measured market share or exclusive control",
        fontsize=10,
        color=SECONDARY,
        ha="left",
        va="bottom",
    )

    fig.savefig(OUT, dpi=160, facecolor=BG, bbox_inches="tight")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
