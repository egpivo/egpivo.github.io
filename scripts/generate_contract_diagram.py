#!/usr/bin/env python3
"""
Generate Contract Architecture diagram (Mermaid + Graphviz) for PAYG service contracts.

Outputs source files (.mmd, .dot) and renders SVG/PNG if renderers are available.

Usage:
  python scripts/generate_contract_diagram.py \
      --out-dir assets/2025-12-11-practicing-solidity-transitioning-to-web3 \
      --png         # optionally also render PNG
      --no-render   # skip rendering, write sources only
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


MERMAID_CONTENT = """%%{init: {
  "themeVariables": { "fontSize": "20px", "fontFamily": "Helvetica" },
  "themeCSS": ".subgraph .label > tspan, .clusterLabel, .cluster .label > tspan { font-size: 22px !important; }\n.edgeLabel tspan { font-size: 16px !important; }"
}}%%
flowchart TB
  %% Classes
  classDef blueprint fill:#E0F2FE,stroke:#0EA5E9,stroke-width:3px,color:#0C4A6E;
  classDef derived fill:#F3E8FF,stroke:#7C3AED,color:#2E1065;
  classDef future fill:#FEF3C7,stroke:#F59E0B,stroke-dasharray: 5 5,color:#4A2C0A;

  BASE["<b>PayAsYouGoBase</b><br/><i>Blueprint / Template</i><br/><br/>Provides core PAYG functionality:<br/>• Service registration<br/>• Payment handling<br/>• Earnings withdrawal"]:::blueprint

  ARTICLE["<b>ArticleSubscription</b><br/><i>Extends Base</i><br/><br/>Adds article-specific features:<br/>• Article publishing<br/>• Read tracking<br/>• Content verification"]:::derived

  FUTURE1["<b>VideoStreaming</b><br/><i>Future Service</i>"]:::future
  FUTURE2["<b>APIAccess</b><br/><i>Future Service</i>"]:::future
  FUTURE3["<b>DataSubscription</b><br/><i>Future Service</i>"]:::future

  BASE -->|"inherits<br/>(blueprint)"| ARTICLE
  BASE -.->|"can extend"| FUTURE1
  BASE -.->|"can extend"| FUTURE2
  BASE -.->|"can extend"| FUTURE3
"""


DOT_CONTENT = """digraph G {
  graph [rankdir=TB, bgcolor=white, fontname="Helvetica", fontsize=14];
  node  [shape=box, style="rounded,filled", fontname="Helvetica"];
  edge  [style=solid, color="#333333", arrowhead=normal];

  BASE [label=<
    <table border="0" cellborder="0" cellspacing="0" cellpadding="4">
      <tr><td><font point-size="26"><b>PayAsYouGoBase</b></font></td></tr>
      <tr><td><font point-size="20" color="#666666"><i>Blueprint / Template</i></font></td></tr>
      <tr><td><font point-size="12"> </font></td></tr>
      <tr><td align="left"><font point-size="18" color="#0C4A6E"><b>Core PAYG Functionality:</b></font></td></tr>
      <tr><td align="left"><font point-size="12"> </font></td></tr>
      <tr><td align="left"><font point-size="16"><b>State:</b></font></td></tr>
      <tr><td align="left">• Service struct (id, price, provider, usageCount)</td></tr>
      <tr><td align="left">• services mapping</td></tr>
      <tr><td align="left">• earnings mapping</td></tr>
      <tr><td align="left">• serviceIds array</td></tr>
      <tr><td><font point-size="12"> </font></td></tr>
      <tr><td align="left"><font point-size="16"><b>Functions:</b></font></td></tr>
      <tr><td align="left">• registerService() - virtual</td></tr>
      <tr><td align="left">• useService() - virtual, payable</td></tr>
      <tr><td align="left">• withdraw() - virtual (CEI pattern)</td></tr>
      <tr><td align="left">• getService() - view</td></tr>
      <tr><td align="left">• getServiceCount() - view</td></tr>
    </table>
  >, fillcolor="#E0F2FE", color="#0EA5E9", penwidth=3, fontcolor="#0C4A6E"];

  ARTICLE [label=<
    <table border="0" cellborder="0" cellspacing="0" cellpadding="4">
      <tr><td><font point-size="24"><b>ArticleSubscription</b></font></td></tr>
      <tr><td><font point-size="18" color="#666666"><i>Extends Blueprint</i></font></td></tr>
      <tr><td><font point-size="12"> </font></td></tr>
      <tr><td align="left"><font point-size="16"><b>Inherits:</b> All base functionality</font></td></tr>
      <tr><td><font point-size="12"> </font></td></tr>
      <tr><td align="left"><font point-size="16"><b>Adds Article-Specific:</b></font></td></tr>
      <tr><td align="left">• Article struct (title, contentHash, publishDate)</td></tr>
      <tr><td align="left">• articles mapping</td></tr>
      <tr><td align="left">• hasRead tracking</td></tr>
      <tr><td align="left">• publishArticle(), readArticle()</td></tr>
    </table>
  >, fillcolor="#F3E8FF", color="#7C3AED", fontcolor="#2E1065"];

  FUTURE1 [label="VideoStreaming\n<i>Future Service</i>", fillcolor="#FEF3C7", color="#F59E0B", style="rounded,filled,dashed", fontcolor="#4A2C0A"];
  FUTURE2 [label="APIAccess\n<i>Future Service</i>", fillcolor="#FEF3C7", color="#F59E0B", style="rounded,filled,dashed", fontcolor="#4A2C0A"];
  FUTURE3 [label="DataSubscription\n<i>Future Service</i>", fillcolor="#FEF3C7", color="#F59E0B", style="rounded,filled,dashed", fontcolor="#4A2C0A"];

  BASE -> ARTICLE [label="inherits\n(blueprint)", fontsize=16, fontcolor="#0C4A6E", penwidth=2];
  BASE -> FUTURE1 [style=dashed, label="can extend", fontsize=14, fontcolor="#666666"];
  BASE -> FUTURE2 [style=dashed, label="can extend", fontsize=14, fontcolor="#666666"];
  BASE -> FUTURE3 [style=dashed, label="can extend", fontsize=14, fontcolor="#666666"];
}
"""


def _run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate()
    return proc.returncode, out, err


def main() -> int:
    p = argparse.ArgumentParser(description="Generate Contract Architecture diagram")
    p.add_argument("--out-dir", default="assets/2025-12-11-practicing-solidity-transitioning-to-web3", help="Output directory")
    p.add_argument("--no-render", action="store_true", help="Write sources only, skip rendering")
    p.add_argument("--png", action="store_true", help="Also render PNG when possible")
    args = p.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    mermaid_path = out / "contract_architecture.mmd"
    dot_path = out / "contract_architecture.dot"
    mermaid_path.write_text(MERMAID_CONTENT, encoding="utf-8")
    dot_path.write_text(DOT_CONTENT, encoding="utf-8")
    print(f"✅ Wrote Mermaid: {mermaid_path}")
    print(f"✅ Wrote Graphviz DOT: {dot_path}")

    if args.no_render:
        print("ℹ️ Skipping rendering (--no-render)")
        return 0

    # Render Graphviz SVG (always available on this machine)
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

