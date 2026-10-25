"""Scrape the public contribution calendar (no token needed) -> data/contributions.json"""
import json
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from config import USERNAME

URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def parse(html):
    soup = BeautifulSoup(html, "html.parser")

    tips = {}  # cell id -> count, from <tool-tip for="cell-id">3 contributions on ...</tool-tip>
    for tip in soup.find_all("tool-tip"):
        m = re.match(r"\s*(No|\d[\d,]*)\s+contribution", tip.get_text(strip=True))
        if m and tip.get("for"):
            tips[tip["for"]] = 0 if m.group(1) == "No" else int(m.group(1).replace(",", ""))

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        date = td.get("data-date")
        if not date:
            continue
        count = tips.get(td.get("id"))
        if count is None:  # older markup fallback
            m = re.search(r"(\d[\d,]*) contribution", td.get_text(" ") + " " + str(td.get("aria-label", "")))
            count = int(m.group(1).replace(",", "")) if m else 0
        days.append({"date": date, "count": count, "level": int(td.get("data-level", 0))})
    days.sort(key=lambda d: d["date"])
    return days


def stats(days):
    total = sum(d["count"] for d in days)

    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)

    i = len(days) - 1
    if i >= 0 and days[i]["count"] == 0:  # today may not have activity yet
        i -= 1
    current = 0
    while i >= 0 and days[i]["count"] > 0:
        current += 1
        i -= 1

    best = max(days, key=lambda d: d["count"])
    monthly = {}
    for d in days:
        monthly[d["date"][:7]] = monthly.get(d["date"][:7], 0) + d["count"]

    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": monthly,
    }


def main():
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 (profile-readme)"}, timeout=30)
    r.raise_for_status()
    days = parse(r.text)
    if not days:
        sys.exit(f"No contribution days found for '{USERNAME}' - check the username in scripts/config.py")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"username": USERNAME, "days": days, **stats(days)}, indent=1), encoding="utf-8")
    print(f"wrote {OUT} ({len(days)} days)")


if __name__ == "__main__":
    main()