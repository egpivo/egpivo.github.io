#!/usr/bin/env python3
"""Fig 1: DFlow share within a DefiLlama Solana aggregator reconstruction."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "data" / "processed" / "dflow_aggregator_share_monthly.csv"
OUT = Path(__file__).resolve().parent / "figure_solana_aggregator_share_over_time.png"

BG = "#F7F6F3"
TEXT = "#2B2B2B"
SECONDARY = "#5F6368"
GRID = "#D9D7D1"
ACQ_FILL = "#6A8F73"
JTX_LINE = "#4C6A91"

COLORS = {
    "Jupiter": "#4C6A91",
    "DFlow": "#6A8F73",
    "Titan": "#B7905E",
    "OKX": "#8A6799",
    "Other": "#9AA0A6",
}

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Arial", "Helvetica", "DejaVu Sans"],
    }
)


def main() -> None:
    months = []
    series = {k: [] for k in COLORS}
    with CSV.open() as f:
        for row in csv.DictReader(f):
            dt = datetime.strptime(row["month"] + "-01", "%Y-%m-%d")
            if dt < datetime(2025, 5, 1) or dt > datetime(2026, 7, 1):
                continue
            months.append(dt)
            series["Jupiter"].append(100.0 * float(row["jupiter_share"]))
            series["DFlow"].append(100.0 * float(row["dflow_share"]))
            series["Titan"].append(100.0 * float(row["titan_share"]))
            series["OKX"].append(100.0 * float(row["okx_share"]))
            series["Other"].append(100.0 * float(row["other_share"]))

    fig, ax = plt.subplots(figsize=(12.4, 6.9), dpi=160)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    # MoonPay acquisition month as a pale green column (DFlow peak passes through)
    may0 = datetime(2026, 5, 1)
    jun0 = datetime(2026, 6, 1)
    ax.axvspan(may0, jun0, color=ACQ_FILL, alpha=0.16, zorder=0, lw=0)

    # JTX synchronized panel window (2026-07-28 to 2026-07-29)
    jtx = datetime(2026, 7, 28)
    ax.axvline(jtx, color=JTX_LINE, linewidth=1.35, linestyle="--", zorder=2, alpha=0.85)

    order = ["Jupiter", "DFlow", "Titan", "OKX", "Other"]
    lw = {"Jupiter": 2.4, "DFlow": 3.0, "Titan": 1.9, "OKX": 1.7, "Other": 1.4}
    z = {"Jupiter": 4, "DFlow": 6, "Titan": 3, "OKX": 2, "Other": 1}
    for name in order:
        ax.plot(
            months,
            series[name],
            color=COLORS[name],
            linewidth=lw[name],
            marker="o",
            markersize=5.0 if name == "DFlow" else (4.2 if name != "Other" else 3.4),
            label=name,
            zorder=z[name],
            alpha=0.96 if name != "Other" else 0.72,
        )

    # Event labels
    ax.text(
        datetime(2026, 5, 16),
        96,
        "May 2026 · MoonPay",
        fontsize=10,
        color=ACQ_FILL,
        ha="center",
        va="top",
        fontweight="bold",
        zorder=7,
    )
    ax.text(
        jtx,
        96,
        "Jul 2026 · JTX panel",
        fontsize=10,
        color=JTX_LINE,
        ha="right",
        va="top",
        fontweight="bold",
        zorder=7,
    )

    # Light narrative markers under the axis story
    ax.text(
        datetime(2025, 10, 1),
        -8,
        "before acquisition",
        fontsize=9,
        color=SECONDARY,
        ha="center",
        va="top",
        clip_on=False,
    )
    ax.text(
        datetime(2026, 6, 15),
        -8,
        "after → measurement",
        fontsize=9,
        color=SECONDARY,
        ha="center",
        va="top",
        clip_on=False,
    )

    ax.set_ylim(0, 100)
    ax.set_xlim(datetime(2025, 4, 20), datetime(2026, 8, 10))
    ax.set_ylabel(
        "Share within reconstructed DefiLlama Solana aggregator volume (%)",
        fontsize=11,
        color=TEXT,
    )
    fig.suptitle(
        "DFlow Share Within a DefiLlama Aggregator Reconstruction",
        fontsize=16,
        color=TEXT,
        fontweight="bold",
        y=0.98,
    )
    ax.set_title(
        "Within-source adoption index · not a verified Blockworks market-share series",
        fontsize=11,
        color=SECONDARY,
        pad=8,
    )

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center", fontsize=10)
    ax.tick_params(colors=SECONDARY)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(GRID)

    for m, s in zip(months, series["DFlow"]):
        if m.year == 2025 and m.month == 9:
            ax.annotate(
                f"{s:.1f}%",
                (m, s),
                textcoords="offset points",
                xytext=(0, 9),
                ha="center",
                fontsize=9,
                color=COLORS["DFlow"],
            )
        if m.year == 2026 and m.month == 5:
            ax.annotate(
                f"{s:.1f}%",
                (m, s),
                textcoords="offset points",
                xytext=(0, -14),
                ha="center",
                fontsize=10,
                fontweight="bold",
                color=COLORS["DFlow"],
            )

    handles = [Line2D([0], [0], color=COLORS[n], lw=2.2, marker="o", markersize=4) for n in order]
    handles.append(Patch(facecolor=ACQ_FILL, edgecolor="none", alpha=0.28, label="MoonPay month"))
    handles.append(
        Line2D([0], [0], color=JTX_LINE, lw=1.4, linestyle="--", label="JTX panel")
    )
    ax.legend(
        handles,
        order + ["MoonPay month", "JTX panel"],
        loc="upper left",
        frameon=False,
        fontsize=10,
        labelcolor=TEXT,
    )

    fig.tight_layout(rect=[0, 0.06, 1, 0.94])
    fig.savefig(OUT, facecolor=BG, bbox_inches="tight")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
