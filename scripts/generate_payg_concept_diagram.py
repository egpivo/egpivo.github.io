#!/usr/bin/env python3
"""
Generate High-Level PAYG Concept Diagram (Mermaid + Graphviz).

This shows the conceptual flow without implementation details.

Usage:
  python scripts/generate_payg_concept_diagram.py \
      --out-dir assets/2025-12-11-practicing-solidity-transitioning-to-web3 \
      --png
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


MERMAID_CONTENT = """%%{init: {
  "themeVariables": { "fontSize": "20px", "fontFamily": "Helvetica" },
  "themeCSS": ".edgeLabel tspan { font-size: 18px !important; }"
}}%%
flowchart LR
  %% Classes
  classDef user fill:#E0F2FE,stroke:#0EA5E9,color:#0C4A6E;
  classDef contract fill:#F3E8FF,stroke:#7C3AED,color:#2E1065;
  classDef provider fill:#DCFCE7,stroke:#16A34A,color:#14532D;
  classDef service fill:#FEF3C7,stroke:#F59E0B,color:#4A2C0A;

  USER["<b>User</b><br/>Wants to use service"]:::user
  CONTRACT["<b>PAYG Contract</b><br/>Handles payment<br/>& access control"]:::contract
  PROVIDER["<b>Service Provider</b><br/>Earns from usage"]:::provider
  SERVICE["<b>Service</b><br/>Article / Video / API<br/>etc."]:::service

  USER -->|"1. pays per use"| CONTRACT
  CONTRACT -->|"2. credits earnings"| PROVIDER
  CONTRACT -->|"3. unlocks access"| SERVICE
  USER -.->|"4. accesses"| SERVICE
"""


DOT_CONTENT = """digraph G {
  graph [rankdir=LR, bgcolor=white, fontname="Helvetica", fontsize=14];
  node  [shape=box, style="rounded,filled", fontname="Helvetica"];
  edge  [style=solid, color="#333333", arrowhead=normal];

  USER [label="User\nWants to use service", fillcolor="#E0F2FE", color="#0EA5E9", fontcolor="#0C4A6E", fontsize=18];
  CONTRACT [label="PAYG Contract\nHandles payment\n& access control", fillcolor="#F3E8FF", color="#7C3AED", fontcolor="#2E1065", fontsize=18];
  PROVIDER [label="Service Provider\nEarns from usage", fillcolor="#DCFCE7", color="#16A34A", fontcolor="#14532D", fontsize=18];
  SERVICE [label="Service\nArticle / Video / API\netc.", fillcolor="#FEF3C7", color="#F59E0B", fontcolor="#4A2C0A", fontsize=18];

  USER -> CONTRACT [label="1. pays per use", fontsize=16, fontcolor="#333333"];
  CONTRACT -> PROVIDER [label="2. credits earnings", fontsize=16, fontcolor="#333333"];
  CONTRACT -> SERVICE [label="3. unlocks access", fontsize=16, fontcolor="#333333"];
  USER -> SERVICE [label="4. accesses", style=dashed, fontsize=16, fontcolor="#666666"];
}
"""


def _run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate()
    return proc.returncode, out, err


def main() -> int:
    p = argparse.ArgumentParser(description="Generate High-Level PAYG Concept Diagram")
    p.add_argument("--out-dir", default="assets/2025-12-11-practicing-solidity-transitioning-to-web3", help="Output directory")
    p.add_argument("--no-render", action="store_true", help="Write sources only, skip rendering")
    p.add_argument("--png", action="store_true", help="Also render PNG when possible")
    args = p.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    mermaid_path = out / "payg_concept.mmd"
    dot_path = out / "payg_concept.dot"
    mermaid_path.write_text(MERMAID_CONTENT, encoding="utf-8")
    dot_path.write_text(DOT_CONTENT, encoding="utf-8")
    print(f"✅ Wrote Mermaid: {mermaid_path}")
    print(f"✅ Wrote Graphviz DOT: {dot_path}")

    if args.no_render:
        print("ℹ️ Skipping rendering (--no-render)")
        return 0

    # Render Graphviz SVG
    dot = shutil.which("dot")
    if dot:
        svg_out = dot_path.with_suffix(".dot.svg")
        code, out_s, err_s = _run([dot, "-Tsvg", str(dot_path), "-o", str(svg_out)])
        if code == 0:
            print(f"✅ Graphviz SVG: {svg_out}")
        else:
            print(f"⚠️ Graphviz SVG render failed: {err_s.strip()}")
        if args.png:
            png_out = dot_path.with_suffix(".dot.png")
            code, out_p, err_p = _run([dot, "-Tpng", str(dot_path), "-o", str(png_out)])
            if code == 0:
                print(f"✅ Graphviz PNG: {png_out}")
            else:
                print(f"⚠️ Graphviz PNG render failed: {err_p.strip()}")
    else:
        print("ℹ️ Graphviz 'dot' not found — skipping Graphviz render")

    # Mermaid (optional)
    mmdc = shutil.which("mmdc")
    if mmdc:
        svg_out = mermaid_path.with_suffix(".mmd.svg")
        code, out_m, err_m = _run([mmdc, "-i", str(mermaid_path), "-o", str(svg_out)])
        if code == 0:
            print(f"✅ Mermaid SVG: {svg_out}")
        else:
            print(f"⚠️ Mermaid render failed: {err_m.strip()}")
    else:
        print("ℹ️ mermaid-cli (mmdc) not found — Mermaid render skipped")

    print("🎉 Done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

