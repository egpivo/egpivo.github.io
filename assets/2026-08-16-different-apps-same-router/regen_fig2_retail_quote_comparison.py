#!/usr/bin/env python3
"""Regenerate Fig. 1 — fee vs quote gap / residual. Debranded labels."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT_PNG = HERE / "figure2_retail_quote_comparison.png"

CSV_CANDIDATES = [
    HERE / "jtx_quote_panel_final.csv",
    Path(
        "/Users/joseph/agentic-research/experiments/jito_jtx_control_plane/"
        "blog_ready/gist/2026-08-16-different-apps-same-router/jtx_quote_panel_final.csv"
    ),
]

BG = "#F7F6F3"
TEXT = "#2B2B2B"
SECONDARY = "#5F6368"
GRID = "#D9D7D1"
REF = "#7A7A7A"

PAIR_ORDER = ["USDC->USDT", "USDC->SOL", "USDC->WETH", "USDC->JUP", "USDC->XAUt0"]
PAIR_SHORT = {
    "USDC->USDT": "USDT",
    "USDC->SOL": "SOL",
    "USDC->WETH": "WETH",
    "USDC->JUP": "JUP",
    "USDC->XAUt0": "XAUt0",
}
COLORS = {
    "USDC->SOL": "#8FB09A",
    "USDC->JUP": "#6B5B7A",
    "USDC->USDT": "#4C6A91",
    "USDC->XAUt0": "#9B8BB0",
    "USDC->WETH": "#A8C5A0",
}

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


def load_panel() -> pd.DataFrame:
    for path in CSV_CANDIDATES:
        if path.is_file():
            df = pd.read_csv(path)
            assert len(df) == 29, len(df)
            return df
    raise FileNotFoundError("jtx_quote_panel_final.csv not found")


def main() -> None:
    df = load_panel()
    residual_cap = 3.2

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(14.2, 5.7),
        dpi=160,
        gridspec_kw={"width_ratios": [1.05, 1.0], "wspace": 0.28},
    )
    fig.patch.set_facecolor(BG)

    # --- Left: fee vs gap (log-log) ---
    ax = axes[0]
    ax.set_facecolor(BG)
    for pair in PAIR_ORDER:
        sub = df[df["pair"] == pair]
        ax.scatter(
            sub["displayed_fee_tier_bps"],
            sub["quote_gap_bps_vs_jupiter"],
            s=55,
            color=COLORS[pair],
            alpha=0.85,
            edgecolors=BG,
            linewidths=0.6,
            zorder=3,
            label=pair.replace("->", "→"),
        )

    lims = [0.7, 40]
    ax.plot(lims, lims, ls="--", color=REF, lw=1.2, zorder=2, label="y = x (gap = displayed fee)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_xlabel("Displayed app fee (bps)", fontsize=12)
    ax.set_ylabel("Quote gap versus outside option (bps)", fontsize=12)
    ax.set_title("Displayed app fee explains most of the quote gap", fontsize=13, color=TEXT, loc="left", pad=10)
    ax.grid(True, which="both", color=GRID, lw=0.6, alpha=0.6)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.text(
        0.02,
        0.02,
        "log scales",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9,
        color=SECONDARY,
        style="italic",
    )

    # --- Right: residual by pair ---
    ax = axes[1]
    ax.set_facecolor(BG)
    x_pos = {p: i for i, p in enumerate(PAIR_ORDER)}
    rng = np.random.default_rng(0)

    for pair in PAIR_ORDER:
        sub = df[df["pair"] == pair]
        x0 = x_pos[pair]
        in_scale = sub[sub["residual_gap_bps"] <= residual_cap]
        off = sub[sub["residual_gap_bps"] > residual_cap]

        if len(in_scale):
            jitter = rng.uniform(-0.12, 0.12, size=len(in_scale))
            ax.scatter(
                np.full(len(in_scale), x0) + jitter,
                in_scale["residual_gap_bps"],
                s=36,
                color=COLORS[pair],
                alpha=0.75,
                edgecolors=BG,
                linewidths=0.5,
                zorder=3,
            )
            y_min, y_max = in_scale["residual_gap_bps"].min(), in_scale["residual_gap_bps"].max()
            ax.plot([x0, x0], [y_min, y_max], color=COLORS[pair], lw=1.4, alpha=0.7, zorder=2)
            med = float(in_scale["residual_gap_bps"].median())
            # include off-scale in median? Caption uses pair medians from full panel.
            med_all = float(sub["residual_gap_bps"].median())
            ax.scatter(
                [x0],
                [med_all],
                marker="D",
                s=70,
                facecolors=COLORS[pair],
                edgecolors=TEXT,
                linewidths=0.9,
                zorder=4,
            )

        for i, (_, row) in enumerate(off.sort_values("residual_gap_bps", ascending=False).iterrows()):
            y_mark = residual_cap - 0.08 - i * 0.28
            ax.scatter(
                [x0],
                [y_mark],
                marker="^",
                s=70,
                color=COLORS[pair],
                edgecolors=TEXT,
                linewidths=0.6,
                zorder=5,
                clip_on=False,
            )
            ax.annotate(
                f"+{row['residual_gap_bps']:.2f}",
                (x0, y_mark),
                textcoords="offset points",
                xytext=(10, 0),
                fontsize=9,
                color=TEXT,
                va="center",
            )

    ax.axhline(0, color=REF, ls="--", lw=1.0, zorder=1)
    ax.set_xticks(list(x_pos.values()))
    ax.set_xticklabels([PAIR_SHORT[p] for p in PAIR_ORDER], fontsize=12)
    ax.set_ylabel("Residual (observed gap − fee-predicted gap, bps)", fontsize=11)
    ax.set_title("Residual quote gap by pair", fontsize=13, color=TEXT, loc="left", pad=10)
    ax.set_ylim(-1.0, residual_cap)
    ax.grid(axis="y", color=GRID, lw=0.6, alpha=0.6)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.text(
        0.98,
        0.02,
        "▲ = off-scale point, value labeled",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        color=SECONDARY,
    )

    fig.savefig(OUT_PNG, dpi=160, facecolor=BG, bbox_inches="tight")
    print(f"wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
