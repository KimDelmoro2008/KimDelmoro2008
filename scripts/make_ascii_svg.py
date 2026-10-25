"""Convert source-prepped.png into a self-typing monochrome ASCII SVG (avi-ascii.svg)."""
from html import escape
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source-prepped.png"
OUT = ROOT / "avi-ascii.svg"

COLS = 100                 # characters per row
FONT = 7                   # px
CW, LH = 4.2, 7.0          # char advance / line height (px)
RAMP = " .`:-=+*cs#%@"     # bright (sparse) -> dark (dense); leading space clears background
ROW_STAGGER = 0.045        # seconds between rows
WIPE = 0.9                 # seconds for one row to print
START = 0.3


def to_lines(img):
    rows = max(1, round(COLS * img.height / img.width * (CW / LH)))
    img = img.convert("L").resize((COLS, rows), Image.LANCZOS)
    px = img.load()
    n = len(RAMP) - 1
    lines = []
    for y in range(rows):
        line = ""
        for x in range(COLS):
            t = ((255 - px[x, y]) / 255) ** 0.9
            line += RAMP[min(n, round(t * n))]
        lines.append(line.rstrip())
    return lines


def main():
    if not SRC.exists():
        raise SystemExit("source-prepped.png not found - run prep_photo.py first")
    lines = to_lines(Image.open(SRC))
    W, H = COLS * CW, len(lines) * LH

    defs, body = [], []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        begin = START + i * ROW_STAGGER
        y = i * LH
        defs.append(
            f'<clipPath id="c{i}"><rect x="0" y="{y:.1f}" width="0" height="{LH}">'
            f'<animate attributeName="width" from="0" to="{W:.1f}" begin="{begin:.3f}s" '
            f'dur="{WIPE}s" fill="freeze"/></rect></clipPath>'
        )
        body.append(
            f'<text clip-path="url(#c{i})" x="0" y="{y + LH - 1.6:.1f}" '
            f'textLength="{len(line) * CW:.1f}" lengthAdjust="spacing" '
            f'xml:space="preserve">{escape(line)}</text>'
        )
        body.append(
            f'<rect class="cur" x="0" y="{y + 0.5:.1f}" width="{CW}" height="{LH - 1}" opacity="0">'
            f'<animate attributeName="x" from="0" to="{W:.1f}" begin="{begin:.3f}s" dur="{WIPE}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0.9;0.9;0" keyTimes="0;0.92;1" '
            f'begin="{begin:.3f}s" dur="{WIPE}s" fill="freeze"/></rect>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}">
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;font-size:{FONT}px;fill:#57606a}}
.cur{{fill:#57606a}}
@media (prefers-color-scheme: dark){{text{{fill:#c9d1d9}}.cur{{fill:#c9d1d9}}}}
</style>
<defs>{"".join(defs)}</defs>
{chr(10).join(body)}
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT} ({COLS}x{len(lines)} chars)")


if __name__ == "__main__":
    main()