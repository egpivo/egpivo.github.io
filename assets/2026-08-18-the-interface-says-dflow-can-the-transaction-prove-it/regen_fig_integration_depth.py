#!/usr/bin/env python3
"""0818 Fig: documented DFlow integration depth (former 0816 Panel A)."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent / "figure_integration_depth.png"

BG = "#F7F6F3"
TEXT = "#2B2B2B"
SECONDARY = "#5F6368"
GRID = "#D9D7D1"
BLUE = "#4C6A91"
GREEN = "#6A8F73"
HIGHLIGHT = "#E8F0E9"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Arial", "Helvetica", "DejaVu Sans"],
    }
)


def rounded(ax, x, y, w, h, fc="#FFFFFF", ec=GRID, lw=0.8, z=1):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.01,rounding_size=0.04",
            facecolor=fc,
            edgecolor=ec,
            linewidth=lw,
            zorder=z,
        )
    )


def main() -> None:
    fig, ax = plt.subplots(figsize=(11.2, 6.4), dpi=160)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    ax.text(
        5,
        9.55,
        "Documented integration depth",
        fontsize=17,
        color=TEXT,
        fontweight="bold",
        ha="center",
    )
    ax.text(
        5,
        9.05,
        "Public API / tooling surface · this capture opens step 3",
        fontsize=11,
        color=SECONDARY,
        ha="center",
    )

    steps = [
        ("Named integration", False),
        ("Quote API", False),
        ("Ready-to-sign transaction", True),
        ("Transaction submission", False),
        ("Streaming / monitoring", False),
        ("Agent-facing tooling", False),
    ]
    y0 = 8.15
    for i, (label, highlight) in enumerate(steps):
        y = y0 - i * 1.15
        rounded(
            ax,
            0.35,
            y - 0.36,
            4.6,
            0.72,
            fc=HIGHLIGHT if highlight else "#FFFFFF",
            ec=GREEN if highlight else GRID,
            lw=1.4 if highlight else 0.8,
        )
        ax.text(
            0.55,
            y,
            f"{i + 1}.  {label}",
            fontsize=12,
            color=TEXT,
            va="center",
            fontweight="bold" if highlight else "normal",
        )
        if highlight:
            ax.text(4.7, y, "← this article", fontsize=10, color=GREEN, va="center", ha="right")
        if i < len(steps) - 1:
            ax.annotate(
                "",
                xy=(2.55, y - 0.88),
                xytext=(2.55, y - 0.58),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.2, mutation_scale=10),
            )

    rounded(ax, 5.2, 0.7, 4.5, 7.7)
    ax.text(5.45, 7.95, "Evidence (docs / claims)", fontsize=12, color=TEXT, fontweight="bold")
    evidence = [
        ("Distribution", "500+ applications (company)"),
        ("Major surfaces", "Coinbase, Phantom,\nSolflare, Kamino"),
        ("Tx construction", "quote → sign → submit"),
        ("Product breadth", "spot + prediction markets"),
        ("Agent interface", "CLI / MCP / Helius skill"),
        ("This capture", "unsigned ready-to-sign tx\n· not submitted"),
    ]
    ey = 7.25
    for title, body in evidence:
        color = GREEN if title == "This capture" else BLUE
        ax.text(5.45, ey, title, fontsize=11, color=color, fontweight="bold", va="top")
        ax.text(5.45, ey - 0.36, body, fontsize=11, color=SECONDARY, va="top", linespacing=1.25)
        ey -= 1.12

    fig.savefig(OUT, dpi=160, facecolor=BG, bbox_inches="tight", pad_inches=0.2)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
