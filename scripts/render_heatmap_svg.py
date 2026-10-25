"""Render data/contributions.json as an animated 53x7 contribution heatmap -> contrib-heatmap.svg"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

CELL, PITCH = 12, 15
LEFT, TOP = 40, 34
W = 860
LIGHT = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39", "#0b3d1e"]
DARK = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]  # none -> neon top end
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    days = data["days"]
    offset = (date.fromisoformat(days[0]["date"]).weekday() + 1) % 7  # Sunday = row 0
    weeks = (len(days) + offset - 1) // 7 + 1
    top_count = max(d["count"] for d in days) or 1

    cells = []
    month_labels, last_month, last_x = [], None, -99
    for i, d in enumerate(days):
        w, r = divmod(i + offset, 7)
        x, y = LEFT + w * PITCH, TOP + r * PITCH
        level = min(d["level"], 4)
        if level == 4 and d["count"] >= 0.75 * top_count:
            level = 5
        delay = (w + r) * 0.015
        n = d["count"]
        tip = f'{n} contribution{"" if n == 1 else "s"} on {d["date"]}'
        cells.append(
            f'<rect class="c l{level}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
            f'style="animation-delay:{delay:.3f}s"><title>{tip}</title></rect>'
        )
        if r == 0:
            m = int(d["date"][5:7])
            if m != last_month:
                if x - last_x >= 3 * PITCH:
                    month_labels.append(f'<text class="t" x="{x}" y="{TOP - 10}">{MONTHS[m - 1]}</text>')
                    last_x = x
                last_month = m

    day_labels = "".join(
        f'<text class="t" x="{LEFT - 8}" y="{TOP + r * PITCH + 10}" text-anchor="end">{name}</text>'
        for r, name in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )

    grid_end = LEFT + weeks * PITCH - (PITCH - CELL)
    base_y = TOP + 7 * PITCH + 24
    legend_x = grid_end - (6 * PITCH + 62)
    legend = f'<text class="t" x="{legend_x}" y="{base_y}">Less</text>' + "".join(
        f'<rect class="l{k}" x="{legend_x + 32 + k * PITCH}" y="{base_y - 10}" width="{CELL}" height="{CELL}" rx="3"/>'
        for k in range(6)
    ) + f'<text class="t" x="{legend_x + 32 + 6 * PITCH + 4}" y="{base_y}">More</text>'

    best = data["best_day"]
    footer = (
        f'{data["total"]:,} contributions in the last year  |  current streak {data["current_streak"]}d  |  '
        f'longest {data["longest_streak"]}d  |  best day {best["count"]}'
    )
    H = base_y + 22

    ramp_light = "".join(f".l{k}{{fill:{c}}}" for k, c in enumerate(LIGHT))
    ramp_dark = "".join(f".l{k}{{fill:{c}}}" for k, c in enumerate(DARK))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>
.t{{font:11px ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;fill:#57606a}}
{ramp_light}
@media (prefers-color-scheme: dark){{.t{{fill:#8b949e}}{ramp_dark}}}
.c{{animation:drop .5s ease-out both}}
@keyframes drop{{from{{opacity:0;transform:translateY(-10px)}}to{{opacity:1;transform:none}}}}
</style>
{"".join(month_labels)}{day_labels}
{chr(10).join(cells)}
<text class="t" x="{LEFT}" y="{base_y}">{footer}</text>
{legend}
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()