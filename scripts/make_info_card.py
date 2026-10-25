"""Hand-authored neofetch-style info card -> info-card.svg

Edit the ROWS list below. Keep values short (~38 characters per line).
Set STATIC=1 for a frozen frame:  $env:STATIC=1; python scripts/make_info_card.py
"""
import os
from html import escape
from pathlib import Path

from config import HANDLE

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

W = 490
TITLE = f"{HANDLE}@github"

# (key, [lines])  <- EDIT THESE
ROWS = [
    ("Now", ["First-year college student"]),
    ("Goal", ["Cloud engineer"]),
    ("Prev", ["Senior high school"]),
    ("Stack", ["Python, Git, HTML/CSS/JS"]),
    ("Highlights", ["Built CofeLang, a student cafe site", "Learning Linux and cloud basics"]),
]

LINE = 22
X_KEY, X_VAL = 24, 138


def main():
    items = []  # (kind, key_class, text, x)
    items.append(("head", "", TITLE, X_KEY))
    items.append(("rule", "", "-" * (len(TITLE) + 2), X_KEY))
    items.append(("gap", "", "", 0))
    for n, (key, vals) in enumerate(ROWS):
        for j, v in enumerate(vals):
            items.append(("row", f"k{n % 4}", (key + ":") if j == 0 else "", X_KEY))
            items.append(("val", "", v, X_VAL))

    y = 66
    out, order = [], 0
    for kind, cls, text, x in items:
        if kind == "gap":
            y += LINE // 2
            continue
        yy = y  # a "val" shares the line of the "row" key before it
        delay = 0.4 + order * 0.16
        style = "" if STATIC else f' style="animation-delay:{delay:.2f}s"'
        klass = {"head": "hd", "rule": "ru", "row": cls, "val": "tx"}[kind]
        if text:
            out.append(f'<text class="ln {klass}" x="{x}" y="{yy}"{style} xml:space="preserve">{escape(text)}</text>')
        if kind in ("val", "head", "rule"):
            y += LINE
        if kind != "row":
            order += 1
    H = max(y + 18, 340)

    anim = "" if STATIC else (
        ".ln{animation:in .45s ease-out both}"
        "@keyframes in{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}"
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>
.win{{fill:#f6f8fa;stroke:#d0d7de}} .bar{{fill:#eaeef2}}
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;font-size:13px}}
.tx{{fill:#24292f}} .hd{{fill:#24292f;font-weight:bold}} .ru{{fill:#8c959f}} .ttl{{fill:#57606a;font-size:12px}}
.k0{{fill:#0969da;font-weight:bold}} .k1{{fill:#8250df;font-weight:bold}}
.k2{{fill:#1a7f37;font-weight:bold}} .k3{{fill:#bc4c00;font-weight:bold}}
@media (prefers-color-scheme: dark){{
.win{{fill:#0d1117;stroke:#30363d}} .bar{{fill:#161b22}}
.tx{{fill:#c9d1d9}} .hd{{fill:#f0f6fc}} .ru{{fill:#484f58}} .ttl{{fill:#8b949e}}
.k0{{fill:#58a6ff}} .k1{{fill:#bc8cff}} .k2{{fill:#3fb950}} .k3{{fill:#ffa657}}
}}
{anim}
</style>
<rect class="win" x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8"/>
<path class="bar" d="M1 9a8 8 0 0 1 8-8h{W - 18}a8 8 0 0 1 8 8v26H1z"/>
<circle cx="20" cy="18" r="5" fill="#ff5f56"/><circle cx="38" cy="18" r="5" fill="#ffbd2e"/><circle cx="56" cy="18" r="5" fill="#27c93f"/>
<text class="ttl" x="{W // 2}" y="22" text-anchor="middle">{escape(TITLE)} - neofetch</text>
{chr(10).join(out)}
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT}{' (static)' if STATIC else ''}")


if __name__ == "__main__":
    main()