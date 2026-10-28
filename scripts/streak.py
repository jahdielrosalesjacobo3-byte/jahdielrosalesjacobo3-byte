#!/usr/bin/env python3
"""Generate a custom streak card (streak.svg) that keeps counting up every day.

The streak is anchored so that it reads BASE_STREAK on ANCHOR_DATE and grows by
one for every day after that. Run daily via .github/workflows/streak.yml.
"""
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

ANCHOR_DATE = dt.date(2026, 10, 27)  # day the streak reads BASE_STREAK
BASE_STREAK = 1563
# Total contributions = streak days + this offset (edit to taste).
TOTAL_OFFSET = 0

# Palette taken from the previous github-readme-streak-stats card.
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


def build_svg(today: dt.date) -> str:
    streak = BASE_STREAK + max(0, (today - ANCHOR_DATE).days)
    start = today - dt.timedelta(days=streak - 1)
    total = streak + TOTAL_OFFSET
    curr_range = f"{fmt_date(start)} - {fmt_date(today, with_year=False)}"
    longest_range = f"{fmt_date(start)} - Present"
    total_range = f"{fmt_date(start)} - Present"

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
    {col(196.67, f"{total:,}", "Total Contributions", total_range, 0.6)}
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
    args = parser.parse_args()
    today = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_svg(today), encoding="utf-8")
    print(f"Wrote {out} for {today}")


if __name__ == "__main__":
    main()
