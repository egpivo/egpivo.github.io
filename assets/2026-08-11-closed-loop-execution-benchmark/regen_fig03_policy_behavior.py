#!/usr/bin/env python3
"""Regenerate fig03 from amm-lab action logs (same logic as m3_figures.py)."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA = Path("/Users/joseph/amm-lab/data/rl_equilibrium")
OUT = Path(__file__).resolve().parent / "fig03_policy_behavior.png"

BG = "#F7F6F3"
TEXT = "#2B2B2B"
GRID = "#D9D7D1"
DQN = "#4C6A91"
LOOKAHEAD = "#8A6799"

GAP_BINS = [(-1e9, -20), (-20, -5), (-5, 5), (5, 20), (20, 1e9)]
GAP_LABELS = ["<-20", "-20..-5", "-5..5", "5..20", ">20"]
FEE_BINS = [(-1e9, -10), (-10, -2), (-2, 2), (2, 10), (10, 1e9)]
FEE_LABELS = ["<-10", "-10..-2", "-2..2", "2..10", ">10"]
TRADE_ACTIONS = {"1", "2", "3", "4", "5", "6"}
ROUTE_A = {"1", "3", "5"}


def load_rows() -> pd.DataFrame:
    fine = pd.read_csv(DATA / "m3_fine_actions.csv")
    dqn = pd.read_csv(DATA / "m3_dqn_actions.csv")
    rows = pd.concat([fine, dqn], ignore_index=True)
    return rows[(rows["mode"] == "DynamicDuopoly") & (rows["policy"].isin(["dqn", "lookahead"]))]


def wait_curve(rows: pd.DataFrame, policy: str) -> list[float]:
    sub = rows[rows["policy"] == policy]
    shares = []
    for lo, hi in GAP_BINS:
        sel = sub[
            (sub["min_oracle_gap_bps"] >= lo)
            & (sub["min_oracle_gap_bps"] < hi)
            & (sub["remaining_frac"] > 1e-6)
        ]
        if len(sel) == 0:
            shares.append(float("nan"))
            continue
        waits = (sel["action"].astype(str) == "0").sum()
        shares.append(waits / len(sel))
    return shares


def route_curve(rows: pd.DataFrame, policy: str) -> list[float]:
    sub = rows[rows["policy"] == policy]
    shares = []
    for lo, hi in FEE_BINS:
        sel = sub[
            (sub["buy_fee_gap_bps"] >= lo)
            & (sub["buy_fee_gap_bps"] < hi)
            & (sub["action"].astype(str).isin(TRADE_ACTIONS))
        ]
        if len(sel) == 0:
            shares.append(float("nan"))
            continue
        routed_a = sel["action"].astype(str).isin(ROUTE_A).sum()
        shares.append(routed_a / len(sel))
    return shares


def main() -> None:
    rows = load_rows()
    wait_dqn = wait_curve(rows, "dqn")
    wait_la = wait_curve(rows, "lookahead")
    route_dqn = route_curve(rows, "dqn")
    route_la = route_curve(rows, "lookahead")

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
        "State-conditional execution behavior on development seeds",
        fontsize=22,
        fontweight="semibold",
        color=TEXT,
        y=0.98,
    )

    for ax in axes:
        ax.grid(axis="y", color=GRID, linewidth=0.8, alpha=0.9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(GRID)
        ax.spines["bottom"].set_color(GRID)

    x_gap = range(len(GAP_LABELS))
    axes[0].plot(x_gap, wait_dqn, marker="o", color=DQN, linewidth=2.2, label="DQN")
    axes[0].plot(
        x_gap, wait_la, marker="o", color=LOOKAHEAD, linewidth=2.2, label="Tuned lookahead"
    )
    axes[0].set_title("Waiting vs oracle gap", fontsize=17, pad=12)
    axes[0].set_xlabel("Best pool oracle gap (bps; negative = pool cheap)")
    axes[0].set_ylabel("Wait share (remaining > 0)")
    axes[0].set_xticks(list(x_gap), GAP_LABELS)
    axes[0].set_ylim(0.35, 0.85)
    axes[0].legend(frameon=False, loc="upper left")

    x_fee = range(len(FEE_LABELS))
    axes[1].plot(x_fee, route_dqn, marker="o", color=DQN, linewidth=2.2, label="DQN")
    axes[1].plot(
        x_fee, route_la, marker="o", color=LOOKAHEAD, linewidth=2.2, label="Tuned lookahead"
    )
    axes[1].set_title("Routing vs fee gap", fontsize=17, pad=12)
    axes[1].set_xlabel("Buy fee gap A−B (bps; negative = A cheaper)")
    axes[1].set_ylabel("Share of single-pool trades routed to A")
    axes[1].set_xticks(list(x_fee), FEE_LABELS)
    axes[1].set_ylim(-0.05, 1.05)
    axes[1].legend(frameon=False, loc="upper right")

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(OUT, bbox_inches="tight", facecolor=BG)
    print(f"wrote {OUT}")
    print("wait DQN:", [round(v, 3) for v in wait_dqn])
    print("wait LA:", [round(v, 3) for v in wait_la])
    print("route DQN:", [round(v, 3) for v in route_dqn])
    print("route LA:", [round(v, 3) for v in route_la])


if __name__ == "__main__":
    main()
