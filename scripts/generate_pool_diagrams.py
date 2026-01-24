#!/usr/bin/env python3
"""
Generate three professional diagrams for Pool Protocol article:
1. Membership Direction Diagram
2. Money Flow + Settlement Diagram  
3. State Transition Diagram (Before/After)

Usage:
  python scripts/generate_pool_diagrams.py --out-dir assets/2025-12-31-payg-pool-protocol-composition-layer
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


# Figure 1: Membership Direction Diagram
MEMBERSHIP_DIRECTION_DOT = """digraph MembershipDirection {
  graph [
    rankdir=TB,
    bgcolor="#f8f9fa",
    fontname="Inter, sans-serif",
    fontsize=14,
    nodesep=1.2,
    ranksep=1.5,
    margin=0.5
  ];
  
  node [
    shape=box,
    style="rounded,filled",
    fontname="Inter, sans-serif",
    fontsize=12,
    margin="0.4,0.3"
  ];
  
  edge [
    color="#6b7280",
    penwidth=2,
    arrowsize=0.8
  ];

  // Pool (center)
  pool [
    label="Creator Membership Pool\nPrice: 1 ETH / 30 days\nMembers: 3 providers",
    fillcolor="#1e40af",
    fontcolor=white,
    fontsize=14,
    style="rounded,filled,bold",
    height=1.2,
    width=3
  ];

  // Providers (top)
  writerA [
    label="Writer A\nshares = 1",
    fillcolor="#dbeafe",
    fontcolor="#1e40af",
    style="rounded,filled"
  ];
  
  writerB [
    label="Writer B\nshares = 2",
    fillcolor="#dbeafe",
    fontcolor="#1e40af",
    style="rounded,filled"
  ];
  
  writerC [
    label="Writer C\nshares = 1",
    fillcolor="#dbeafe",
    fontcolor="#1e40af",
    style="rounded,filled"
  ];

  providersLabel [
    label="Pool Members (Payees)",
    shape=plaintext,
    fontsize=11,
    fontcolor="#6b7280"
  ];

  {rank=same; writerA; writerB; writerC}
  {rank=max; providersLabel}

  // User (bottom)
  alice [
    label="Alice\nUser (Payer)\nBuys access\nNOT a member",
    fillcolor="#f3f4f6",
    fontcolor="#374151",
    style="rounded,filled"
  ];

  userLabel [
    label="User (Payer)",
    shape=plaintext,
    fontsize=11,
    fontcolor="#6b7280"
  ];

  {rank=min; userLabel; alice}

  // Edges
  providersLabel -> writerA [style=invis];
  writerA -> pool [label="revenue split", fontsize=10, fontcolor="#6b7280"];
  writerB -> pool [label="revenue split", fontsize=10, fontcolor="#6b7280"];
  writerC -> pool [label="revenue split", fontsize=10, fontcolor="#6b7280"];
  
  alice -> pool [label="payment (1 ETH)", fontsize=10, fontcolor="#059669", penwidth=2.5];
  
  userLabel -> alice [style=invis];
}
"""

# Figure 2: Money Flow + Settlement Diagram
MONEY_FLOW_DOT = """digraph MoneyFlow {
  graph [
    rankdir=LR,
    bgcolor="#f8f9fa",
    fontname="Inter, sans-serif",
    fontsize=13,
    nodesep=1.5,
    ranksep=2.0,
    margin=0.5
  ];
  
  node [
    shape=box,
    style="rounded,filled",
    fontname="Inter, sans-serif",
    margin="0.4,0.3"
  ];
  
  edge [
    color="#6b7280",
    penwidth=3,
    arrowsize=0.9
  ];

  // User (left)
  alice [
    label="Alice\nPays 1 ETH",
    fillcolor="#e0e7ff",
    fontcolor="#3730a3",
    style="rounded,filled,bold",
    fontsize=13
  ];

  // Pool Contract (center)
  pool [
    label="Pool Contract\nOperator fee: 2%\nNet: 0.98 ETH",
    fillcolor="#1e40af",
    fontcolor=white,
    style="rounded,filled,bold",
    fontsize=13,
    height=1.5
  ];

  // Operator (above pool)
  operator [
    label="Operator\n0.02 ETH",
    fillcolor="#fef3c7",
    fontcolor="#92400e",
    style="rounded,filled",
    fontsize=12
  ];

  // Providers (right)
  writerA [
    label="Writer A\n0.245 ETH",
    fillcolor="#dbeafe",
    fontcolor="#1e40af",
    style="rounded,filled",
    fontname="'Fira Code', monospace"
  ];
  
  writerB [
    label="Writer B\n0.490 ETH",
    fillcolor="#dbeafe",
    fontcolor="#1e40af",
    style="rounded,filled",
    fontname="'Fira Code', monospace"
  ];
  
  writerC [
    label="Writer C\n0.245 ETH",
    fillcolor="#dbeafe",
    fontcolor="#1e40af",
    style="rounded,filled",
    fontname="'Fira Code', monospace"
  ];

  {rank=same; writerA; writerB; writerC}
  {rank=max; operator}

  // Edges
  alice -> pool [label="1 ETH", fontsize=12, fontcolor="#059669", penwidth=4];
  pool -> operator [label="0.02 ETH", fontsize=11, fontcolor="#92400e", penwidth=3];
  pool -> writerA [label="0.245 ETH", fontsize=11, fontcolor="#1e40af", penwidth=2.5];
  pool -> writerB [label="0.490 ETH", fontsize=11, fontcolor="#1e40af", penwidth=2.5];
  pool -> writerC [label="0.245 ETH", fontsize=11, fontcolor="#1e40af", penwidth=2.5];
}
"""

# Figure 3: State Transition Diagram (Before/After)
STATE_TRANSITION_DOT = """digraph StateTransition {
  graph [
    rankdir=LR,
    bgcolor="#f8f9fa",
    fontname="Inter, sans-serif",
    fontsize=12,
    nodesep=2.0,
    ranksep=1.5,
    margin=0.5
  ];
  
  node [
    shape=box,
    style="rounded",
    fontname="Inter, sans-serif",
    margin="0.4,0.3"
  ];
  
  edge [
    color="#6b7280",
    penwidth=2.5,
    arrowsize=0.9
  ];

  // Before state
  before [
    label=<
      <table border="0" cellborder="1" cellspacing="0" cellpadding="8" bgcolor="#f3f4f6">
        <tr><td align="left"><b>Pool #12</b></td></tr>
        <tr><td align="left">usageCount = 0</td></tr>
        <tr><td align="left"><br/></td></tr>
        <tr><td align="left"><b>Access:</b></td></tr>
        <tr><td align="left">Alice → ❌</td></tr>
        <tr><td align="left"><br/></td></tr>
        <tr><td align="left"><b>Earnings:</b></td></tr>
        <tr><td align="left">A: 0</td></tr>
        <tr><td align="left">B: 0</td></tr>
        <tr><td align="left">C: 0</td></tr>
        <tr><td align="left">Operator: 0</td></tr>
      </table>
    >,
    style="rounded",
    fillcolor="#f3f4f6",
    fontcolor="#374151",
    fontsize=11
  ];

  beforeLabel [
    label="Before purchase",
    shape=plaintext,
    fontsize=13,
    fontcolor="#6b7280",
    fontweight=bold
  ];

  // Transaction arrow
  transaction [
    label="purchasePool()\n1 ETH",
    shape=box,
    style="rounded,filled",
    fillcolor="#1e40af",
    fontcolor=white,
    fontsize=12,
    height=1.5
  ];

  // After state
  after [
    label=<
      <table border="0" cellborder="1" cellspacing="0" cellpadding="8" bgcolor="#ecfdf5">
        <tr><td align="left"><b>Pool #12</b></td></tr>
        <tr><td align="left">usageCount = 1</td></tr>
        <tr><td align="left"><br/></td></tr>
        <tr><td align="left"><b>Access:</b></td></tr>
        <tr><td align="left">Alice → ✅ valid until T+30d</td></tr>
        <tr><td align="left"><br/></td></tr>
        <tr><td align="left"><b>Earnings:</b></td></tr>
        <tr><td align="left">Operator: +0.02 ETH</td></tr>
        <tr><td align="left">A: +0.245 ETH</td></tr>
        <tr><td align="left">B: +0.490 ETH</td></tr>
        <tr><td align="left">C: +0.245 ETH</td></tr>
      </table>
    >,
    style="rounded",
    fillcolor="#ecfdf5",
    fontcolor="#065f46",
    fontsize=11
  ];

  afterLabel [
    label="After purchase",
    shape=plaintext,
    fontsize=13,
    fontcolor="#059669",
    fontweight=bold
  ];

  {rank=same; before; transaction; after}
  {rank=max; beforeLabel; afterLabel}

  // Edges
  beforeLabel -> before [style=invis];
  afterLabel -> after [style=invis];
  before -> transaction [style=invis];
  transaction -> after;
}
"""


def _run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate()
    return proc.returncode, out, err


def main() -> int:
    p = argparse.ArgumentParser(description="Generate Pool Protocol diagrams")
    p.add_argument("--out-dir", default="assets/2025-12-31-payg-pool-protocol-composition-layer", help="Output directory")
    p.add_argument("--no-render", action="store_true", help="Write source only, skip rendering")
    p.add_argument("--png", action="store_true", help="Also render PNG when possible")
    args = p.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    diagrams = [
        ("membership_direction", MEMBERSHIP_DIRECTION_DOT, "Membership Direction Diagram"),
        ("money_flow", MONEY_FLOW_DOT, "Money Flow + Settlement Diagram"),
        ("state_transition", STATE_TRANSITION_DOT, "State Transition Diagram"),
    ]

    dot = shutil.which("dot")
    
    for filename, dot_content, desc in diagrams:
        dot_path = out / f"{filename}.dot"
        dot_path.write_text(dot_content, encoding="utf-8")
        print(f"✅ Wrote {desc}: {dot_path}")

        if args.no_render:
            continue

        if dot:
            # Render SVG
            svg_out = dot_path.with_suffix(".svg")
            code, out_s, err_s = _run([dot, "-Tsvg", str(dot_path), "-o", str(svg_out)])
            if code == 0:
                print(f"   ✅ SVG: {svg_out}")
            else:
                print(f"   ⚠️ SVG render failed: {err_s.strip()}")
            
            # Render PNG if requested
            if args.png:
                png_out = dot_path.with_suffix(".png")
                code, out_p, err_p = _run([dot, "-Tpng", "-Gdpi=150", str(dot_path), "-o", str(png_out)])
                if code == 0:
                    print(f"   ✅ PNG: {png_out}")
                else:
                    print(f"   ⚠️ PNG render failed: {err_p.strip()}")
        else:
            print("   ℹ️ Graphviz 'dot' not found — skipping render")

    print("🎉 Done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




