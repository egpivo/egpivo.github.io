#!/usr/bin/env bash
set -euo pipefail

die() { echo "error: $*" >&2; exit 1; }

MD="${1:-}"
[[ -n "$MD" ]] || die "usage: $(basename "$0") <path/to/file.md> [output.pdf]"

MD_ABS="$(cd "$(dirname "$MD")" && pwd)/$(basename "$MD")"
[[ -f "$MD_ABS" ]] || die "not a file: $MD_ABS"

DIR="$(dirname "$MD_ABS")"
FILE="$(basename "$MD_ABS")"
OUT_ARG="${2:-}"

if [[ -n "$OUT_ARG" ]]; then
  if [[ "$OUT_ARG" == */* ]]; then
    OUT_ABS="$(cd "$(dirname "$OUT_ARG")" && pwd)/$(basename "$OUT_ARG")"
  else
    OUT_ABS="$(pwd)/$OUT_ARG"
  fi
else
  OUT_ABS="${MD_ABS%.md}.pdf"
fi

command -v pandoc >/dev/null 2>&1 || die "pandoc not found (brew install pandoc)"

ENGINE="${MD_PDF_ENGINE:-}"
if [[ -z "$ENGINE" ]]; then
  for e in xelatex lualatex pdflatex; do
    if command -v "$e" >/dev/null 2>&1; then
      ENGINE="$e"
      break
    fi
  done
fi
[[ -n "$ENGINE" ]] || die "no pdf engine (xelatex/lualatex/pdflatex). Install BasicTeX/MacTeX."

cd "$DIR"

if [[ "${GEN_FIGURES:-0}" == 1 ]] && [[ -f generate_blog_figures.py ]]; then
  echo "GEN_FIGURES=1: running python3 generate_blog_figures.py"
  python3 generate_blog_figures.py
fi

# Strip Jekyll {{ site.baseurl }} and convert HTML <img> to markdown ![](path)
SITE_ROOT="$(cd "$DIR/.." && pwd)"
TMP1="/tmp/blog_pdf_stage1_$$.md"
TMP_MD="/tmp/blog_pdf_$$.md"

sed "s|{{ site.baseurl }}|${SITE_ROOT}|g" "$FILE" > "$TMP1"

python3 -c "
import re, sys
site_root = sys.argv[3]
with open(sys.argv[1]) as f:
    content = f.read()

def abs_assets(path: str) -> str:
    if path.startswith('/assets/'):
        return site_root + path
    return path

def replace_img(m):
    src = re.search(r'src=\"([^\"]+)\"', m.group(0))
    alt = re.search(r'alt=\"([^\"]+)\"', m.group(0))
    src_path = abs_assets(src.group(1)) if src else ''
    return '![{}]({})'.format(alt.group(1) if alt else '', src_path)

content = re.sub(r'<img\s[^>]+/?>', replace_img, content)
content = re.sub(
    r'!\[([^\]]*)\]\((/assets/[^)]+)\)',
    lambda m: f'![{m.group(1)}]({abs_assets(m.group(2))})',
    content,
)
content = content.replace('≠', '$\\neq$')
content = re.sub(r'^(#{1,6}\s+.*)\$\\neq\$', lambda m: m.group(1).replace('$\\neq$', ' is not '), content, flags=re.MULTILINE)
with open(sys.argv[2], 'w') as f:
    f.write(content)
" "$TMP1" "$TMP_MD" "$SITE_ROOT"

rm -f "$TMP1"

pandoc "$TMP_MD" -o "$OUT_ABS" \
  --from=markdown+yaml_metadata_block+smart \
  --resource-path="$DIR:${SITE_ROOT}/assets" \
  --pdf-engine="$ENGINE" \
  -V geometry:margin=1in

rm -f "$TMP_MD"

echo "wrote $OUT_ABS (pandoc + $ENGINE)"
