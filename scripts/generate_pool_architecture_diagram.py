#!/usr/bin/env python3
"""
Generate Pool Protocol Architecture diagram using Graphviz.

This creates a visual representation of the Pool Protocol architecture,
showing how Pool Protocol composes services from different modules.

Usage:
  python scripts/generate_pool_architecture_diagram.py \
      --out-dir assets/2025-12-31-payg-pool-protocol-composition-layer \
      --png         # optionally also render PNG
      --no-render   # skip rendering, write source only
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


DOT_CONTENT = """digraph PoolArchitecture {
  graph [
    rankdir=TB,
    bgcolor=white,
    fontname="Monaco, monospace",
    fontsize=12,
    nodesep=0.5,
    ranksep=0.8,
    margin=0.3
  ];
  
  node [
    shape=box,
    style="rounded",
    fontname="Monaco, monospace",
    fontsize=12,
    margin="0.2,0.1"
  ];
  
  edge [
    color=black,
    penwidth=1.5,
    arrowsize=0.7
  ];

  // Pool Protocol as a cluster with three internal components
  subgraph cluster_pool {
    label="Pool Protocol";
    style="rounded";
    fontname="Monaco, monospace";
    fontsize=14;
    margin=15;
    
    purchase [
      label="Purchase",
      style="rounded"
    ];
    
    split [
      label="Split",
      style="rounded"
    ];
    
    entitlement [
      label="Entitlement",
      style="rounded"
    ];
    
    {rank=same; purchase; split; entitlement}
  }

  // Module boxes (bottom level)
  article [
    label="Article module\n(domain rules)",
    style="rounded"
  ];
  
  rental [
    label="Rental module\n(domain rules)",
    style="rounded"
  ];
  
  future [
    label="Future module\n(domain rules)",
    style="rounded"
  ];
  
  {rank=same; article; rental; future}

  // Edges from Pool Protocol cluster to modules
  purchase -> article [ltail=cluster_pool, constraint=false];
  purchase -> rental [ltail=cluster_pool, constraint=false];
  purchase -> future [ltail=cluster_pool, constraint=false];
}
"""


def _run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate()
    return proc.returncode, out, err


def main() -> int:
    p = argparse.ArgumentParser(description="Generate Pool Protocol Architecture diagram")
    p.add_argument("--out-dir", default="assets/2025-12-28-payg-pool-protocol-composition-layer", help="Output directory")
    p.add_argument("--no-render", action="store_true", help="Write source only, skip rendering")
    p.add_argument("--png", action="store_true", help="Also render PNG when possible")
    args = p.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    dot_path = out / "pool_architecture.dot"
    dot_path.write_text(DOT_CONTENT, encoding="utf-8")
    print(f"✅ Wrote Graphviz DOT: {dot_path}")

    if args.no_render:
        print("ℹ️ Skipping rendering (--no-render)")
        return 0

    # Render Graphviz SVG
    dot = shutil.which("dot")
    if dot:
        svg_out = dot_path.with_suffix(".svg")
        code, out_s, err_s = _run([dot, "-Tsvg", str(dot_path), "-o", str(svg_out)])
        if code == 0:
            print(f"✅ Graphviz SVG: {svg_out}")
        else:
            print(f"⚠️ Graphviz SVG render failed: {err_s.strip()}")
        
        if args.png:
            png_out = dot_path.with_suffix(".png")
            code, out_p, err_p = _run([dot, "-Tpng", "-Gdpi=150", str(dot_path), "-o", str(png_out)])
            if code == 0:
                print(f"✅ Graphviz PNG: {png_out}")
            else:
                print(f"⚠️ Graphviz PNG render failed: {err_p.strip()}")
    else:
        print("ℹ️ Graphviz 'dot' not found — skipping render")

    print("🎉 Done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

