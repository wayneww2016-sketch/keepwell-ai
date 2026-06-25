#!/usr/bin/env python3
"""
Generate a visual HTML weekly wellness report.
Usage: python generate_report.py [--open]
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
HISTORY_DIR = PROJECT_DIR / "history"
OUTPUT_DIR = PROJECT_DIR / "reports"


def get_weekly_data():
    """Load 7 days of history."""
    days = []
    for i in range(6, -1, -1):
        date = datetime.now() - timedelta(days=i)
        f = HISTORY_DIR / f"{date.strftime('%Y-%m-%d')}.json"
        day = {"date": date.strftime("%Y-%m-%d"), "day_name": date.strftime("%a")}
        if f.exists():
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            day["nudges"] = len(data.get("nudges", []))
            day["checkins"] = data.get("checkins", [])
        else:
            day["nudges"] = 0
            day["checkins"] = []
        days.append(day)
    return days


def calculate_averages(days):
    """Calculate dimension averages from check-in data."""
    dims = {}
    for day in days:
        for checkin in day.get("checkins", []):
            for dim, score in checkin.get("scores", {}).items():
                if dim not in dims:
                    dims[dim] = []
                dims[dim].append(score)
    return {d: round(sum(s)/len(s), 1) for d, s in dims.items()}


def generate_html(days, averages):
    """Generate the HTML report."""
    today = datetime.now().strftime("%Y-%m-%d")
    total_nudges = sum(d["nudges"] for d in days)
    total_checkins = sum(len(d["checkins"]) for d in days)

    # Dimension display info
    dim_info = {
        "physical": ("🏃", "#76b900"),
        "emotional": ("💭", "#5b9bd5"),
        "occupational": ("💼", "#8ecb4a"),
        "social": ("🤝", "#4ab4c4"),
        "intellectual": ("📖", "#a78bfa"),
        "environmental": ("🌿", "#38bdf8"),
        "financial": ("💰", "#fbbf24"),
        "spiritual": ("✨", "#f472b6"),
    }

    # Build dimension bars
    dim_bars = ""
    for dim in ["physical", "emotional", "occupational", "social",
                "intellectual", "environmental", "financial", "spiritual"]:
        icon, color = dim_info[dim]
        avg = averages.get(dim, 0)
        pct = avg / 5 * 100
        dim_bars += f"""
        <div class="dim-row">
            <span class="dim-icon">{icon}</span>
            <span class="dim-name">{dim.capitalize()}</span>
            <div class="bar-bg">
                <div class="bar-fill" style="width:{pct}%;background:{color}"></div>
            </div>
            <span class="dim-score">{avg if avg else '—'}</span>
        </div>"""

    # Build activity heatmap
    heatmap = ""
    for day in days:
        intensity = min(day["nudges"] + len(day["checkins"]) * 2, 10)
        opacity = max(0.1, intensity / 10)
        heatmap += f"""
        <div class="heat-cell" style="opacity:{opacity}" title="{day['date']}: {day['nudges']} nudges">
            <div class="heat-day">{day['day_name']}</div>
            <div class="heat-count">{day['nudges']}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KeepWell AI — Weekly Report</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0f1419;color:#e7e9ea;padding:40px 20px;min-height:100vh}}
.container{{max-width:680px;margin:0 auto}}
h1{{font-size:28px;font-weight:700;margin-bottom:4px}}
.subtitle{{color:#71767b;font-size:14px;margin-bottom:32px}}
.card{{background:#1e2732;border-radius:16px;padding:24px;margin-bottom:20px}}
.card h2{{font-size:16px;font-weight:600;margin-bottom:16px;color:#76b900}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px}}
.stat{{text-align:center;background:#1e2732;border-radius:12px;padding:20px}}
.stat-val{{font-size:32px;font-weight:700;color:#76b900}}
.stat-lbl{{font-size:12px;color:#71767b;margin-top:4px}}
.dim-row{{display:flex;align-items:center;gap:8px;margin-bottom:10px}}
.dim-icon{{font-size:18px;width:24px}}
.dim-name{{width:100px;font-size:13px;color:#a0a8b4}}
.bar-bg{{flex:1;height:8px;background:#2e3842;border-radius:4px;overflow:hidden}}
.bar-fill{{height:100%;border-radius:4px;transition:width 0.6s ease}}
.dim-score{{width:30px;text-align:right;font-size:13px;font-weight:600}}
.heatmap{{display:grid;grid-template-columns:repeat(7,1fr);gap:8px}}
.heat-cell{{background:#76b900;border-radius:8px;padding:12px 8px;text-align:center}}
.heat-day{{font-size:11px;font-weight:600;margin-bottom:4px}}
.heat-count{{font-size:18px;font-weight:700}}
.footer{{text-align:center;color:#71767b;font-size:12px;margin-top:32px}}
.footer a{{color:#76b900;text-decoration:none}}
</style>
</head>
<body>
<div class="container">
<h1>🧠 KeepWell AI</h1>
<p class="subtitle">Weekly Wellness Report — {days[0]['date']} to {days[-1]['date']}</p>

<div class="stats">
<div class="stat"><div class="stat-val">{total_nudges}</div><div class="stat-lbl">Nudges This Week</div></div>
<div class="stat"><div class="stat-val">{total_checkins}</div><div class="stat-lbl">Check-ins</div></div>
<div class="stat"><div class="stat-val">{len(averages)}/8</div><div class="stat-lbl">Dimensions Covered</div></div>
</div>

<div class="card">
<h2>Dimension Scores</h2>
{dim_bars}
</div>

<div class="card">
<h2>Activity This Week</h2>
<div class="heatmap">
{heatmap}
</div>
</div>

<div class="footer">
Generated by <a href="https://github.com/wayneww2016-sketch/keepwell-ai">KeepWell AI</a> on {today}
</div>
</div>
</body>
</html>"""
    return html


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate KeepWell weekly HTML report")
    parser.add_argument("--open", action="store_true", help="Open report in browser")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)
    days = get_weekly_data()
    averages = calculate_averages(days)
    html = generate_html(days, averages)

    filename = f"keepwell-report-{datetime.now().strftime('%Y-%m-%d')}.html"
    output_path = OUTPUT_DIR / filename
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  ✓ Report generated: {output_path}")

    if args.open:
        import webbrowser
        webbrowser.open(str(output_path))


if __name__ == "__main__":
    main()
