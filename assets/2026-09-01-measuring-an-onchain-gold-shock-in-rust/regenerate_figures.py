#!/usr/bin/env python3
"""Regenerate PAXG/WTIC on-chain figures from frozen CSVs and shocktrace JSON."""

from __future__ import annotations

import csv
import json
import subprocess
from datetime import date
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).resolve().parent
ENGINE_ROOT = HERE.parents[2] / "shock-to-migration"
PROJECT = "paxg_wtic_reference_2026_07_08"

BG = "#F7F6F3"
TEXT = "#2B2B2B"
SECONDARY = "#5F6368"
GRID = "#D9D7D1"
PAXG = "#3F6F64"
WTIC = "#B45A3C"
EVENT = "#7A7A7A"
REFERENCE = "#7A7A7A"


def configure() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": BG,
            "axes.facecolor": BG,
            "axes.edgecolor": GRID,
            "axes.labelcolor": TEXT,
            "axes.titlecolor": TEXT,
            "xtick.color": SECONDARY,
            "ytick.color": SECONDARY,
            "text.color": TEXT,
            "font.family": "sans-serif",
            "font.sans-serif": ["Inter", "Source Sans 3", "Arial", "DejaVu Sans"],
            "font.size": 12,
            "axes.titlesize": 17,
            "axes.labelsize": 13,
            "legend.fontsize": 10,
        }
    )


def run_measure(args: list[str]) -> dict:
    completed = subprocess.run(
        ["cargo", "run", "-q", "-p", "shocktrace-cli", "--", *args, "--format", "json"],
        cwd=ENGINE_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def load_prices(asset: str) -> dict[date, float]:
    path = ENGINE_ROOT / "projects" / PROJECT / "data" / "response_daily.csv"
    out: dict[date, float] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["asset_key"] == asset and row["price"]:
                out[date.fromisoformat(row["day"])] = float(row["price"])
    return out


def style_axis(ax: plt.Axes) -> None:
    ax.grid(axis="y", color=GRID, linewidth=0.8, alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def fig01_response_gap() -> None:
    paxg = run_measure(
        [
            "measure",
            "response-gap",
            f"projects/{PROJECT}",
            "--asset",
            "PAXG",
            "--reference",
            "GOLD_SPOT",
        ]
    )
    wtic = run_measure(
        [
            "measure",
            "response-gap",
            f"projects/{PROJECT}",
            "--asset",
            "WTIC",
            "--reference",
            "WTI_FRONT_MONTH",
        ]
    )

    rows = [
        ("Gold", float(paxg["reference_return"]) * 100, float(paxg["token_return"]) * 100, "PAXG", PAXG),
        ("Oil", float(wtic["reference_return"]) * 100, float(wtic["token_return"]) * 100, "WTIC", WTIC),
    ]

    fig, ax = plt.subplots(figsize=(10.8, 4.8))
    for y, (group, reference, token, token_label, color) in zip([1, 0], rows):
        ax.plot([reference, token], [y, y], color=GRID, lw=3, zorder=1)
        ax.scatter(reference, y, s=130, color=REFERENCE, marker="o", zorder=2)
        ax.scatter(token, y, s=145, color=color, marker="s", zorder=3)
        ax.text(reference, y + 0.14, f"Benchmark {reference:+.2f}%", ha="center", color=SECONDARY)
        ax.text(token, y - 0.18, f"{token_label} {token:+.2f}%", ha="center", color=color)
        gap = token - reference
        ax.text(
            (reference + token) / 2,
            y + 0.34,
            f"token − benchmark {gap:+.2f} pp",
            ha="center",
            color=TEXT,
            fontsize=11,
        )
        ax.text(-1.42, y, group, va="center", ha="left", color=TEXT, fontsize=13)

    ax.axvline(0, color=EVENT, lw=1.0, ls=":")
    ax.set_xlim(-1.5, 5.1)
    ax.set_ylim(-0.55, 1.55)
    ax.set_yticks([])
    ax.set_xlabel("Event-day return")
    ax.set_title("Token and benchmark directions matched")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:+.0f}%"))
    style_axis(ax)
    fig.tight_layout()
    fig.savefig(HERE / "fig01_response_gap.png", dpi=160)
    plt.close(fig)


def fig01_paths() -> None:
    start, end = date(2026, 6, 24), date(2026, 7, 22)
    series = {
        "PAXG": (load_prices("PAXG"), PAXG, "-"),
        "WTIC": (load_prices("WTIC"), WTIC, "-"),
    }
    anchor_day = date(2026, 7, 7)
    fig, ax = plt.subplots(figsize=(10.8, 5.4))
    for label, (prices, color, ls) in series.items():
        if anchor_day not in prices:
            cands = [d for d in prices if d <= anchor_day]
            if not cands:
                continue
            a = max(cands)
        else:
            a = anchor_day
        days = [d for d in sorted(prices) if start <= d <= end]
        vals = [100.0 * prices[d] / prices[a] for d in days]
        ax.plot(days, vals, color=color, lw=2.0, ls=ls, label=label)
    ax.axvline(date(2026, 7, 8), color=EVENT, ls=":", lw=1.2)
    ax.set_title("The two tokenized markets registered different paths")
    ax.set_ylabel("Indexed to 100 at pre-event mark")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.legend(frameon=False, loc="upper left")
    style_axis(ax)
    fig.tight_layout()
    fig.savefig(HERE / "fig01_onchain_paths.png", dpi=160)
    plt.close(fig)


def fig03_zscores() -> None:
    paxg = run_measure(["measure", "shock", f"projects/{PROJECT}", "--asset", "PAXG"])
    wtic = run_measure(["measure", "shock", f"projects/{PROJECT}", "--asset", "WTIC"])
    div = run_measure(
        [
            "measure",
            "divergence",
            f"projects/{PROJECT}",
            "--asset-a",
            "PAXG",
            "--asset-b",
            "WTIC",
        ]
    )

    z_labels = ["PAXG", "WTIC", "PAXG − WTIC gap"]
    z_values = [
        float(paxg["shock"]["z_score"]),
        float(wtic["shock"]["z_score"]),
        float(div["z_score"]),
    ]
    z_colors = [PAXG, WTIC, "#6B5B6E"]
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    bars = ax.barh(z_labels, z_values, color=z_colors, height=0.58)
    ax.axvline(0, color=GRID, lw=1.0)
    ax.set_title("Event returns relative to frozen baselines")
    ax.set_xlabel("Event-day z-score")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:+.1f}"))
    ax.invert_yaxis()
    for bar, value in zip(bars, z_values):
        ax.text(
            value + 0.07,
            bar.get_y() + bar.get_height() / 2,
            f"{value:+.2f}",
            va="center",
            ha="left",
            color=TEXT,
        )
    style_axis(ax)
    fig.tight_layout()
    fig.savefig(HERE / "fig03_standardized.png", dpi=160)
    plt.close(fig)


def main() -> None:
    configure()
    fig01_response_gap()
    fig01_paths()
    fig03_zscores()
    print("wrote shock and response-gap figures")


if __name__ == "__main__":
    main()
