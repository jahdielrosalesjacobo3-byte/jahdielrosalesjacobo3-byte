#!/usr/bin/env python3
"""Generate a custom streak card (streak.svg).

- Total Contributions: Fetched live and real from GitHub's GraphQL API across all time.
- Current Streak: Custom base (1563 on 2026-10-27) and increments +1 each day automatically.
- Longest Streak: Matches the streak counter.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

USERNAME = "jahdielrosalesjacobo3-byte"
ANCHOR_DATE = dt.date(2026, 10, 27)
BASE_STREAK = 1563

# Palette
BG = "#0a101f"
STROKE = "#22d3ee"
RING = "#a78bfa"
FIRE = "#10b981"
CURR_LABEL = "#22d3ee"
SIDE_LABEL = "#94a3b8"
NUM = "#f8fafc"
DATES = "#64748b"
FONT = "&quot;Segoe UI&quot;, Ubuntu, sans-serif"


def fmt_date(d: dt.date, with_year: bool = True) -> str:
    return f"{d.strftime('%b')} {d.day}, {d.year}" if with_year else f"{d.strftime('%b')} {d.day}"


def fetch_real_contributions(username: str, token: str | None) -> tuple[int, str]:
    """Fetch real all-time contributions using GitHub GraphQL API, or fallback to known real count."""
    default_total = 118
    default_range = "Aug 15, 2025 - Present"
    if not token:
        return default_total, default_range

    try:
        headers = {"Authorization": f"Bearer {token}", "User-Agent": "streak-script"}
        q1 = f"""query {{ user(login: "{username}") {{ createdAt }} }}"""
        req1 = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": q1}).encode(),
            headers=headers,
        )
        with urllib.request.urlopen(req1, timeout=10) as resp:
            d1 = json.loads(resp.read().decode())
        created_at_str = d1["data"]["user"]["createdAt"]
        created_date = dt.datetime.fromisoformat(created_at_str.replace("Z", "+00:00")).date()
        start_year = created_date.year
        this_year = dt.date.today().year

        subqueries = []
        for y in range(start_year, this_year + 1):
            subqueries.append(
                f"""y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z") {{ contributionCalendar {{ totalContributions }} }}"""
            )

        q2 = f"""query {{ user(login: "{username}") {{ {" ".join(subqueries)} }} }}"""
        req2 = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": q2}).encode(),
            headers=headers,
        )
        with urllib.request.urlopen(req2, timeout=10) as resp:
            d2 = json.loads(resp.read().decode())

        real_total = sum(
            d2["data"]["user"][f"y{y}"]["contributionCalendar"]["totalContributions"]
            for y in range(start_year, this_year + 1)
        )
        date_range = f"{fmt_date(created_date)} - Present"
        return real_total, date_range
    except Exception as e:
        print(f"Warning: could not fetch real contributions via GraphQL: {e}")
        return default_total, default_range


def build_svg(today: dt.date, real_total: int, total_range: str) -> str:
    streak = BASE_STREAK + max(0, (today - ANCHOR_DATE).days)
    streak_start = today - dt.timedelta(days=streak - 1)
    curr_range = f"{fmt_date(streak_start)} - {fmt_date(today, with_year=False)}"
    longest_range = f"{fmt_date(streak_start)} - Present"

    def col(x: float, num: str, label: str, rng: str, delay: float) -> str:
        return f"""
    <g transform='translate({x}, 48)'>
      <text x='0' y='32' text-anchor='middle' fill='{NUM}' font-family='{FONT}' font-weight='700' font-size='28px' style='opacity:0;animation:fadein .5s linear forwards {delay}s'>{num}</text>
    </g>
    <g transform='translate({x}, 84)'>
      <text x='0' y='32' text-anchor='middle' fill='{SIDE_LABEL}' font-family='{FONT}' font-size='14px' style='opacity:0;animation:fadein .5s linear forwards {delay + 0.1:.1f}s'>{label}</text>
    </g>
    <g transform='translate({x}, 114)'>
      <text x='0' y='32' text-anchor='middle' fill='{DATES}' font-family='{FONT}' font-size='12px' style='opacity:0;animation:fadein .5s linear forwards {delay + 0.2:.1f}s'>{rng}</text>
    </g>"""

    return f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1180 195' width='1180px' height='195px' style='isolation:isolate' direction='ltr'>
  <style>
    @keyframes currstreak {{ 0% {{ font-size:3px; opacity:.2; }} 80% {{ font-size:34px; opacity:1; }} 100% {{ font-size:28px; opacity:1; }} }}
    @keyframes fadein {{ 0% {{ opacity:0; }} 100% {{ opacity:1; }} }}
  </style>
  <defs>
    <clipPath id='outer'><rect width='1180' height='195' rx='4.5'/></clipPath>
    <mask id='ringmask'>
      <rect width='1180' height='195' fill='white'/>
      <ellipse cx='590' cy='32' rx='13' ry='18' fill='black'/>
    </mask>
  </defs>
  <g clip-path='url(#outer)'>
    <rect fill='{BG}' rx='4.5' x='0.5' y='0.5' width='1179' height='194'/>
    <line x1='393.33' y1='28' x2='393.33' y2='170' stroke-width='1' stroke='{STROKE}'/>
    <line x1='786.67' y1='28' x2='786.67' y2='170' stroke-width='1' stroke='{STROKE}'/>
    {col(196.67, f"{real_total:,}", "Total Contributions", total_range, 0.6)}
    <g transform='translate(590, 48)'>
      <text x='0' y='32' text-anchor='middle' fill='{NUM}' font-family='{FONT}' font-weight='700' font-size='28px' style='animation:currstreak .6s linear forwards'>{streak:,}</text>
    </g>
    <g transform='translate(590, 108)'>
      <text x='0' y='32' text-anchor='middle' fill='{CURR_LABEL}' font-family='{FONT}' font-weight='700' font-size='14px' style='opacity:0;animation:fadein .5s linear forwards .9s'>Current Streak</text>
    </g>
    <g transform='translate(590, 145)'>
      <text x='0' y='21' text-anchor='middle' fill='{DATES}' font-family='{FONT}' font-size='12px' style='opacity:0;animation:fadein .5s linear forwards .9s'>{curr_range}</text>
    </g>
    <g mask='url(#ringmask)'>
      <circle cx='590' cy='71' r='40' fill='none' stroke='{RING}' stroke-width='5' style='opacity:0;animation:fadein .5s linear forwards .4s'/>
    </g>
    <g transform='translate(590, 19.5)' style='opacity:0;animation:fadein .5s linear forwards .6s'>
      <path d='M 1.5 0.67 C 1.5 0.67 2.24 3.32 2.24 5.47 C 2.24 7.53 0.89 9.2 -1.17 9.2 C -3.23 9.2 -4.79 7.53 -4.79 5.47 L -4.76 5.11 C -6.78 7.51 -8 10.62 -8 13.99 C -8 18.41 -4.42 22 0 22 C 4.42 22 8 18.41 8 13.99 C 8 8.6 5.41 3.79 1.5 0.67 Z M -0.29 19 C -2.07 19 -3.51 17.6 -3.51 15.86 C -3.51 14.24 -2.46 13.1 -0.7 12.74 C 1.07 12.38 2.9 11.53 3.92 10.16 C 4.31 11.45 4.51 12.81 4.51 14.2 C 4.51 16.85 2.36 19 -0.29 19 Z' fill='{FIRE}'/>
    </g>
    {col(983.33, f"{streak:,}", "Longest Streak", longest_range, 1.2)}
  </g>
</svg>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="dist/streak.svg")
    parser.add_argument("--date", help="Override today's date (YYYY-MM-DD)")
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN"), help="GitHub token for GraphQL")
    args = parser.parse_args()

    today = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    real_total, total_range = fetch_real_contributions(USERNAME, args.token)
    print(f"Real contributions: {real_total} ({total_range})")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_svg(today, real_total, total_range), encoding="utf-8")
    print(f"Wrote {out} for {today}")


if __name__ == "__main__":
    main()
