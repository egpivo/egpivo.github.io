#!/usr/bin/env python3
"""Fig. 2 evidence matrix — simplified two-column version."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle

OUT = Path(__file__).resolve().parent / "figure2_evidence_matrix.png"

BG = "#F7F6F3"
TEXT = "#2B2B2B"
SECONDARY = "#5F6368"
GRID = "#D9D7D1"
GREEN = "#6A8F73"
ORANGE = "#B7905E"
PURPLE = "#6B5B7A"
ROW_ALT = "#FBFAF7"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Arial", "Helvetica", "DejaVu Sans"],
    }
)

# Quote vs compiled tx only. Runtime stays in prose.
# marks: Quote / API, Compiled tx
ROWS = [
    ('Router label “DFlow”', ("check", "dash")),
    ("Program address DF1ow4…", ("dash", "check")),
    ('Registry name “DFlow Aggregator v4”', ("dash", "ext")),
    ("Quote metadata (ID, routePlan, fee)", ("check", "dash")),
    ("Instruction bytes / amounts", ("half", "half")),
]

COLS = ["Quote / API", "Compiled tx"]


def draw_mark(ax, x, y, kind: str) -> None:
    if kind == "check":
        ax.plot(x, y, marker="$\u2713$", markersize=14, color=GREEN, linestyle="None")
    elif kind == "dash":
        ax.plot([x - 0.16, x + 0.16], [y, y], color=SECONDARY, lw=1.9, solid_capstyle="round")
    elif kind == "half":
        ax.add_patch(Circle((x, y), 0.14, facecolor=ORANGE, edgecolor=ORANGE, lw=1.0, zorder=3))
        ax.add_patch(
            FancyBboxPatch(
                (x, y - 0.15),
                0.16,
                0.30,
                boxstyle="square,pad=0",
                facecolor=BG,
                edgecolor="none",
                zorder=4,
            )
        )
        ax.add_patch(Circle((x, y), 0.14, facecolor="none", edgecolor=ORANGE, lw=1.3, zorder=5))
    elif kind == "ext":
        ax.text(x, y, "ext", ha="center", va="center", fontsize=10, color=PURPLE, fontweight="bold")


def main() -> None:
    n = len(ROWS)
    fig, ax = plt.subplots(figsize=(10.0, 5.0), dpi=160)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 10)
    # Leave clear gap under the last row box before the legend.
    ax.set_ylim(-1.55, n + 0.85)
    ax.axis("off")

    ax.text(0.2, n + 0.4, "What Survived Compilation?", fontsize=17, color=TEXT, fontweight="bold")

    col_x = [6.2, 8.4]
    for cx, title in zip(col_x, COLS):
        ax.text(cx, n - 0.05, title, ha="center", va="center", fontsize=12, color=SECONDARY)

    for i, (label, marks) in enumerate(ROWS):
        y = n - 1.0 - i
        ax.add_patch(
            FancyBboxPatch(
                (0.15, y - 0.34),
                9.55,
                0.68,
                boxstyle="round,pad=0.01,rounding_size=0.05",
                facecolor=BG if i % 2 == 0 else ROW_ALT,
                edgecolor=GRID,
                linewidth=0.7,
            )
        )
        ax.text(0.35, y, label, ha="left", va="center", fontsize=12, color=TEXT)
        for cx, mk in zip(col_x, marks):
            draw_mark(ax, cx, y, mk)

    # Last row sits at y=0 with box bottom at -0.34; keep legend well below.
    ly = -1.05
    ax.text(0.35, ly, "Legend", ha="left", va="center", fontsize=9, color=SECONDARY, fontweight="bold")
    legend = [
        (1.35, "check", "visible"),
        (3.1, "half", "opaque"),
        (4.7, "dash", "not recovered"),
        (6.85, "ext", "external registry"),
    ]
    for x, kind, lab in legend:
        draw_mark(ax, x, ly, kind)
        ax.text(x + 0.26, ly, lab, ha="left", va="center", fontsize=9, color=SECONDARY)

    fig.savefig(OUT, dpi=160, facecolor=BG, bbox_inches="tight", pad_inches=0.15)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
