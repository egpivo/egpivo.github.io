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

python3 - "$TMP1" "$TMP_MD" "$SITE_ROOT" <<'PYEOF'
import re, sys

tmp_in, tmp_out, site_root = sys.argv[1], sys.argv[2], sys.argv[3]
with open(tmp_in, encoding='utf-8') as f:
    content = f.read()

def abs_assets(path):
    if path.startswith('/assets/'):
        return site_root + path
    return path

def replace_img(m):
    src = re.search(r'src="([^"]+)"', m.group(0))
    alt = re.search(r'alt="([^"]+)"', m.group(0))
    src_path = abs_assets(src.group(1)) if src else ''
    return '![{}]({})'.format(alt.group(1) if alt else '', src_path)

content = re.sub(r'<img\s[^>]+/?>', replace_img, content)
content = re.sub(
    r'!\[([^\]]*)\]\((/assets/[^)]+)\)',
    lambda m: '![{}]({})'.format(m.group(1), abs_assets(m.group(2))),
    content,
)

# ---------------------------------------------------------------------------
# Unicode subscript/superscript/Greek -> real LaTeX math.
# PDF text fonts routinely lack the actual "t-subscript", "O-superscript" ...
# glyphs (Latin Subscript / Phonetic Extensions blocks), so render these as
# genuine TeX sub/superscripts instead: they then draw from the math font,
# not the body font, and survive any --mainfont choice.
# ---------------------------------------------------------------------------
GREEK = {
    'α': r'\alpha', 'β': r'\beta', 'γ': r'\gamma', 'δ': r'\delta',
    'ε': r'\varepsilon', 'ζ': r'\zeta', 'η': r'\eta', 'θ': r'\theta',
    'ι': r'\iota', 'κ': r'\kappa', 'λ': r'\lambda', 'μ': r'\mu',
    'ν': r'\nu', 'ξ': r'\xi', 'ο': 'o', 'π': r'\pi',
    'ρ': r'\rho', 'σ': r'\sigma', 'τ': r'\tau', 'υ': r'\upsilon',
    'φ': r'\varphi', 'χ': r'\chi', 'ψ': r'\psi', 'ω': r'\omega',
    'Α': 'A', 'Β': 'B', 'Γ': r'\Gamma', 'Δ': r'\Delta',
    'Ε': 'E', 'Ζ': 'Z', 'Η': 'H', 'Θ': r'\Theta', 'Ι': 'I',
    'Κ': 'K', 'Λ': r'\Lambda', 'Μ': 'M', 'Ν': 'N',
    'Ξ': r'\Xi', 'Ο': 'O', 'Π': r'\Pi', 'Ρ': 'P',
    'Σ': r'\Sigma', 'Τ': 'T', 'Υ': r'\Upsilon', 'Φ': r'\Phi',
    'Χ': 'X', 'Ψ': r'\Psi', 'Ω': r'\Omega',
}
OPERATORS = {
    '∑': r'\sum', '∏': r'\prod', '∫': r'\int', '∼': r'\sim',
    # '√' deliberately excluded: \sqrt requires a brace-wrapped argument,
    # which simple token concatenation can't supply correctly (it already
    # renders fine as a literal glyph, so leave it untouched).
}
SUB = {
    '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
    '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
    'ₐ': 'a', 'ₑ': 'e', 'ₕ': 'h', 'ᵢ': 'i', 'ⱼ': 'j',
    'ₖ': 'k', 'ₗ': 'l', 'ₘ': 'm', 'ₙ': 'n', 'ₒ': 'o',
    'ₚ': 'p', 'ᵣ': 'r', 'ₛ': 's', 'ₜ': 't', 'ᵤ': 'u',
    'ᵥ': 'v', 'ₓ': 'x',
    '₊': '+', '₋': '-', '₌': '=', '₍': '(', '₎': ')',
}
SUP = {
    '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
    '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
    'ⁿ': 'n', 'ⁱ': 'i',
    '⁺': '+', '⁻': '-', '⁼': '=', '⁽': '(', '⁾': ')',
    'ᴬ': 'A', 'ᴮ': 'B', 'ᴰ': 'D', 'ᴱ': 'E', 'ᴳ': 'G',
    'ᴴ': 'H', 'ᴵ': 'I', 'ᴶ': 'J', 'ᴷ': 'K', 'ᴸ': 'L',
    'ᴹ': 'M', 'ᴺ': 'N', 'ᴼ': 'O', 'ᴾ': 'P', 'ᴿ': 'R',
    'ᵀ': 'T', 'ᵁ': 'U', 'ⱽ': 'V', 'ᵂ': 'W',
    'ᵃ': 'a', 'ᵇ': 'b', 'ᶜ': 'c', 'ᵈ': 'd', 'ᵉ': 'e',
    'ᶠ': 'f', 'ᵍ': 'g', 'ʰ': 'h', 'ʲ': 'j', 'ᵏ': 'k',
    'ˡ': 'l', 'ᵐ': 'm', 'ᵒ': 'o', 'ᵖ': 'p', 'ʳ': 'r',
    'ˢ': 's', 'ᵗ': 't', 'ᵘ': 'u', 'ᵛ': 'v', 'ʷ': 'w',
    'ˣ': 'x', 'ʸ': 'y', 'ᶻ': 'z',
}
# Mathematical Alphanumeric Symbols (italic), e.g. the U+1D44F "b" in b_t.
MATH_ITALIC = {}
for _i in range(26):
    MATH_ITALIC[chr(0x1D434 + _i)] = chr(ord('A') + _i)  # italic capitals
    MATH_ITALIC[chr(0x1D44E + _i)] = chr(ord('a') + _i)  # italic lowercase

TRIGGER_CHARS = set(SUB) | set(SUP) | set(GREEK) | set(OPERATORS) | set(MATH_ITALIC)

def kind_of(ch):
    if ch in SUB:
        return 'sub'
    if ch in SUP:
        return 'sup'
    return 'base'

def base_value(ch):
    if ch in GREEK:
        return GREEK[ch]
    if ch in OPERATORS:
        return OPERATORS[ch]
    return MATH_ITALIC[ch]

def render_group(kind, mapped_chars):
    val = ''.join(mapped_chars)
    marker = '_' if kind == 'sub' else '^'
    return marker + val if len(val) == 1 else marker + '{' + val + '}'

def convert_math_tokens(text):
    out = []
    i, n = 0, len(text)
    while i < n:
        base_start = i
        j = i
        while j < n and (j - base_start) < 4 and text[j].isascii() and text[j].isalnum():
            j += 1
        k = j
        groups = []
        cur_kind, cur_chars = None, []
        while k < n and text[k] in TRIGGER_CHARS:
            ch = text[k]
            ck = kind_of(ch)
            if ck != cur_kind:
                if cur_chars:
                    groups.append((cur_kind, cur_chars))
                cur_kind, cur_chars = ck, []
            cur_chars.append(ch)
            k += 1
        if cur_chars:
            groups.append((cur_kind, cur_chars))

        if groups:
            tex = text[base_start:j]
            for gk, gchars in groups:
                if gk == 'base':
                    tex += ''.join(base_value(c) for c in gchars)
                else:
                    mapped = [(SUB if gk == 'sub' else SUP)[c] for c in gchars]
                    tex += render_group(gk, mapped)
            out.append('${}$'.format(tex))
            i = k
        else:
            out.append(text[i])
            i += 1
    return ''.join(out)

# Skip fenced/inline code: never rewrite variable-looking text inside code.
# Placeholders use Private-Use-Area delimiters so they can never collide
# with an ordinary number (date, percentage, dollar amount, ...) in prose.
CODE_RE = re.compile(r'```.*?```|`[^`\n]*`', re.DOTALL)
_stash = []
_OPEN, _CLOSE = '\uE000', '\uE001'
_SENTINEL_RE = re.compile(_OPEN + r'(\d+)' + _CLOSE)

def _protect(m):
    _stash.append(m.group(0))
    return _OPEN + str(len(_stash) - 1) + _CLOSE

protected = CODE_RE.sub(_protect, content)
protected = convert_math_tokens(protected)
content = _SENTINEL_RE.sub(lambda m: _stash[int(m.group(1))], protected)

content = content.replace('≠', '$\\neq$')

# Jekyll/Kramdown needs "\\$" in the source so MathJax's processEscapes sees
# a literal "\$" survive into the HTML (Kramdown strips one backslash level).
# Pandoc's markdown reader strips backslash-escapes differently: it wants a
# single "\$" to emit a clean dollar sign in the PDF, and a doubled "\\$"
# prints a visible backslash character. Normalize for the PDF path only.
content = content.replace('\\\\$', '\\$')

content = re.sub(
    r'^(#{1,6}\s+.*)\$\\neq\$',
    lambda m: m.group(1).replace('$\\neq$', ' is not '),
    content,
    flags=re.MULTILINE,
)
with open(tmp_out, 'w', encoding='utf-8') as f:
    f.write(content)
PYEOF

rm -f "$TMP1"

FONT_ARGS=()
if [[ -n "${MD_PDF_MAINFONT:-}" ]]; then
  FONT_ARGS+=(-V "mainfont=${MD_PDF_MAINFONT}")
fi

pandoc "$TMP_MD" -o "$OUT_ABS" \
  --from=markdown+yaml_metadata_block+smart \
  --resource-path="$DIR:${SITE_ROOT}/assets" \
  --pdf-engine="$ENGINE" \
  -V geometry:margin=1in \
  "${FONT_ARGS[@]+"${FONT_ARGS[@]}"}"

rm -f "$TMP_MD"

echo "wrote $OUT_ABS (pandoc + $ENGINE)"
