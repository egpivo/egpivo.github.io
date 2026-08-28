#!/usr/bin/env python3
"""Forum draft v6 figures (publication candidate) — simplified pass.

Each figure answers exactly one question, at a 3-5 second read. Technical
qualification (denominator meaning, candidate-set vs. participation, the
label-availability split, registry provenance) lives in the post's prose and
figure captions, not on the chart — with three exceptions that stay on-image
because a screenshotted figure would otherwise mislead on its own:
denominators, the point/candidate-set distinction, and the routing-decision
row reading as an absence rather than a 0% bar.

fig1: field-level recoverability (how much is recoverable).
fig2: registry sensitivity - same evidence set, two interpretation layers
      (how sensitive is the number to the registry).
fig3: evidence -> interpretation -> claim, commitment band disconnected
      (where does the evidence for each claim come from).

Inputs are frozen Stage 2 conservative-registry results:
  stage2/output/population_transparency_estimates.json
  stage2/output/v4_decomposition.json
No numbers are computed here; they are transcribed from those artifacts.
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parent

BG = "#F7F6F3"
TEXT = "#2B2B2B"
MUTED = "#6E6A63"
RULE = "#D8D3CA"

IV = "#4C6A91"         # independently attributed / in the record
ABSTAIN = "#C29A63"    # abstained: unmapped venue semantics
ABSTAIN_D = "#8F6E42"  # darker tint: external-attribution step
POOL_PT = "#5F8468"    # point identified
POOL_SET = "#A3C0AA"   # candidate set narrowed
POOL_NONE = "#BDB6AA"  # neither
RESOLVE = "#7C8CA1"    # resolution layer (measurement design)
STRUCT = "#8A8A8A"     # not written to the record


def setup():
    plt.rcParams.update({
        "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Source Sans 3", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "text.color": TEXT,
    })


# --------------------------------------------------------------------------- fig 1

def fig1():
    setup()
    fig, ax = plt.subplots(figsize=(13.5, 7.6), dpi=170)
    ax.set_xlim(-40, 108)
    ax.set_ylim(-4, 60)
    ax.axis("off")

    ax.text(-40, 56.5, "Field-level recoverability", fontsize=26, fontweight="600",
            color=TEXT, ha="left")
    ax.text(-40, 52.2, "SPYx x OKX router, 21-24 June 2026 (N = 6,695)",
            fontsize=13.5, color=MUTED, ha="left")

    H = 6.6

    def seg_label(x0, w, text, dark, y, above=False):
        cx = x0 + w / 2
        if not above and w >= 20:
            ax.text(cx, y, text, ha="center", va="center", fontsize=14.5,
                    fontweight="600", color="#FFFFFF" if dark else TEXT, zorder=3)
        else:
            ax.text(cx, y + H / 2 + 2.4, text, ha="center", va="bottom",
                    fontsize=12.5, fontweight="600", color=TEXT, zorder=3)
            ax.plot([cx, cx], [y + H / 2, y + H / 2 + 1.8], color=MUTED,
                    linewidth=1, zorder=3)

    def row(y, name, denom, segments):
        ax.text(-40, y + 1.6, name, fontsize=17, color=TEXT, ha="left", va="center")
        ax.text(-40, y - 2.6, denom, fontsize=12, color=MUTED, ha="left", va="center")
        x = 0.0
        for w, color, text, dark, *rest in segments:
            above = bool(rest and rest[0])
            ax.add_patch(plt.Rectangle((x, y - H / 2), w, H, facecolor=color,
                                       edgecolor=BG, linewidth=1.4, zorder=2))
            seg_label(x, w, text, dark, y, above=above)
            x += w

    row(43.5, "Settlement", "N = 6,695",
        [(100.0, IV, "100%", True)])

    row(28.0, "Route / source class", "N = 6,695",
        [(69.86, IV, "69.9% attributed", True),
         (30.14, ABSTAIN, "30.1% abstained", False)])

    row(12.5, "Public pool provenance", "N = 4,687",
        [(43.48, POOL_PT, "43.5% point", True),
         (41.26, POOL_SET, "41.3% candidate set", False),
         (15.25, POOL_NONE, "15.3% neither", False, True)])

    y4 = -1.0
    ax.text(-40, y4 + 1.6, "Routing decision", fontsize=17, color=TEXT, ha="left", va="center")
    ax.text(-40, y4 - 2.6, "—", fontsize=12, color=MUTED, ha="left", va="center")
    ax.add_patch(plt.Rectangle((0, y4 - H / 2), 100, H, facecolor="none",
                               edgecolor=STRUCT, linewidth=1.5, linestyle=(0, (5, 4)),
                               hatch="///", zorder=2))
    ax.text(50, y4, "not in landed record", ha="center", va="center", fontsize=14,
            color="#4F4F4F", zorder=3, bbox=dict(facecolor=BG, edgecolor="none", pad=3.5))

    fig.subplots_adjust(left=0.24, right=0.97, top=0.96, bottom=0.03)
    p = OUT / "fig1_identifiability_ladder_v6.png"
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    print("wrote", p)


# --------------------------------------------------------------------------- fig 2

def fig2():
    """Registry sensitivity: same evidence set, two interpretation layers.

    Numbers transcribed from stage2/output/registry_sensitivity.json
    (conservative_iv_frac 0.6986, expanded_iv_frac 1.0). The added segment is
    one hatched block: no `external_only` registry tier has been frozen, so
    the external / census-derived split inside it is NOT quantified here.
    """
    setup()
    fig, ax = plt.subplots(figsize=(13, 6.4), dpi=170)
    ax.set_xlim(-30, 116)
    ax.set_ylim(-6, 40)
    ax.axis("off")

    ax.text(-30, 36.5, "Same evidence, different interpretation layer",
            fontsize=25, fontweight="600", color=TEXT, ha="left")
    ax.text(-30, 32.4, "Route / source attribution, SPYx x OKX census",
            fontsize=13.5, color=MUTED, ha="left")

    H = 7.4
    y1, y2 = 22.0, 8.0

    ax.text(-30, y1, "R_conservative", fontsize=16.5, color=TEXT, ha="left", va="center")
    ax.add_patch(plt.Rectangle((0, y1 - H / 2), 69.86, H, facecolor=IV,
                               edgecolor="none", zorder=2))
    ax.text(72.5, y1, "69.86%", va="center", fontsize=17, fontweight="600", color=TEXT)

    ax.text(-30, y2, "R_expanded", fontsize=16.5, color=TEXT, ha="left", va="center")
    ax.add_patch(plt.Rectangle((0, y2 - H / 2), 69.86, H, facecolor=IV,
                               edgecolor="none", zorder=2))
    ax.add_patch(plt.Rectangle((69.86, y2 - H / 2), 30.14, H, facecolor="#F2E9DC",
                               edgecolor=ABSTAIN_D, linewidth=1.4, hatch="///", zorder=2))
    ax.text(102.5, y2, "100.00%", va="center", fontsize=17, fontweight="600", color=TEXT)
    ax.text(85.0, y2, "+30.14 pp", ha="center", va="center", fontsize=11.8,
            fontweight="600", color=ABSTAIN_D, zorder=3,
            bbox=dict(facecolor="#F2E9DC", edgecolor="none", pad=1.5))
    ax.text(85.0, y2 - H / 2 - 2.8, "census-derived mappings included",
            ha="center", va="top", fontsize=10.8, color=ABSTAIN_D, style="italic")

    ax.plot([69.86, 69.86], [y1 - H / 2, y2 + H / 2], color=IV,
            linewidth=1.3, linestyle=(0, (3, 3)), zorder=1)

    fig.subplots_adjust(left=0.20, right=0.97, top=0.94, bottom=0.03)
    p = OUT / "fig2_registry_sensitivity_v6.png"
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    print("wrote", p)


# --------------------------------------------------------------------------- fig 3

def _box(ax, cx, cy, w, h, text, *, edge, face, dashed=False, fontsize=12.5,
         weight="normal", color=TEXT):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0.5,rounding_size=1.4",
        facecolor=face, edgecolor=edge, linewidth=1.5,
        linestyle=(0, (5, 3)) if dashed else "solid", zorder=2))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fontsize,
            color=color, fontweight=weight, zorder=3)


def _arrow(ax, p0, p1, color, dashed=False):
    ax.add_patch(FancyArrowPatch(
        p0, p1, arrowstyle="-|>", mutation_scale=13, linewidth=1.5, color=color,
        linestyle=(0, (4, 3)) if dashed else "solid",
        shrinkA=3, shrinkB=3, zorder=1))


def fig3():
    """Evidence ownership map. No percentages, no legend, no remedy table —
    those live in Fig. 1 and section 6 of the post. This figure answers one
    question: where does the evidence for each claim come from."""
    setup()
    fig, ax = plt.subplots(figsize=(14, 9.0), dpi=170)
    ax.set_xlim(0, 138)
    ax.set_ylim(-4, 78)
    ax.axis("off")

    ax.text(2, 74, "Where the evidence for each claim comes from",
            fontsize=24, fontweight="600", color=TEXT)

    ax.text(20, 65.5, "LANDED RECORD", fontsize=11.5, fontweight="600",
            color=IV, ha="center")
    ax.text(69, 65.5, "INTERPRETATION", fontsize=11.5, fontweight="600",
            color=MUTED, ha="center")
    ax.text(120, 65.5, "CLAIM", fontsize=11.5, fontweight="600",
            color=MUTED, ha="center")

    # row A - settlement: evidence terminates directly at the claim
    yA = 55
    _box(ax, 20, yA, 34, 8, "router + balances", edge=IV, face="#E7ECF3")
    _arrow(ax, (37, yA), (103, yA), IV)
    ax.text(120, yA, "Settlement", ha="center", va="center", fontsize=14.5,
            fontweight="600", color=IV)

    # row B - route class: needs an external attribution step
    yB = 38
    _box(ax, 20, yB, 34, 10, "programs + CPI\nlogs / Dex events", edge=IV, face="#E7ECF3")
    _arrow(ax, (37, yB), (56, yB), ABSTAIN_D, dashed=True)
    _box(ax, 69, yB, 26, 8, "external\nattribution", edge=ABSTAIN_D, face="#F2E9DC",
         dashed=True, fontsize=11.8)
    _arrow(ax, (82, yB), (103, yB), ABSTAIN_D, dashed=True)
    ax.text(120, yB, "Route class", ha="center", va="center", fontsize=14.5,
            fontweight="600", color=ABSTAIN_D)

    # row C - pool provenance: needs both account evidence and a resolution rule
    yC = 21
    _box(ax, 20, yC, 34, 8, "declared accounts", edge=IV, face="#E7ECF3")
    _arrow(ax, (37, yC), (56, yC), RESOLVE, dashed=True)
    _box(ax, 69, yC, 26, 10, "pool metadata\n+ resolution rule", edge=RESOLVE,
         face="#E9ECF0", dashed=True, fontsize=11.4)
    _arrow(ax, (82, yC), (103, yC), RESOLVE, dashed=True)
    ax.text(120, yC, "Pool provenance", ha="center", va="center", fontsize=14.5,
            fontweight="600", color=RESOLVE)

    # off-record band
    ax.plot([2, 136], [12.5, 12.5], color=RULE, linewidth=1.2)
    ax.text(69, 9.4, "OFF-RECORD / NOT COMMITTED", fontsize=11.5, fontweight="600",
            color="#4F4F4F", ha="center")
    _box(ax, 34, 3.4, 60, 6.4, "unsubmitted alternatives", edge=STRUCT, face=BG,
         dashed=True, color="#4F4F4F", fontsize=12)
    _box(ax, 104, 3.4, 60, 6.4, "RFQ / decision context", edge=STRUCT, face=BG,
         dashed=True, color="#4F4F4F", fontsize=12)

    fig.subplots_adjust(left=0.01, right=0.99, top=0.97, bottom=0.02)
    p = OUT / "fig3_evidence_layers_v6.png"
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    print("wrote", p)


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
