#!/usr/bin/env python3
"""
KeepWell AI — Evidence-based well-being nudges for knowledge workers.
CLI tool for delivering context-aware wellness tips across 8 dimensions.

Usage:
    python keepwell.py                     # Time-aware random nudge
    python keepwell.py --dimension physical # Specific dimension
    python keepwell.py --all               # One tip per dimension
    python keepwell.py --weekly-reflection  # Weekly self-assessment prompt
    python keepwell.py --list-dimensions   # List all 8 dimensions
"""

import json
import random
import argparse
import os
from datetime import datetime
from pathlib import Path


def load_tips(lang="en"):
    """Load the wellbeing tips database."""
    if lang == "zh" or lang == "zh-TW":
        filename = "wellbeing-tips-zh.json"
    else:
        filename = "wellbeing-tips.json"
    data_path = Path(__file__).parent.parent / "data" / filename
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_time_period():
    """Determine current time period based on circadian rhythm."""
    hour = datetime.now().hour
    if 5 <= hour < 9:
        return "morning"
    elif 9 <= hour < 12:
        return "deep_work"
    elif 12 <= hour < 14:
        return "midday"
    elif 14 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 21:
        return "evening"
    elif 21 <= hour < 23:
        return "wind_down"
    else:
        return "late_night"


def get_time_appropriate_dimensions(period):
    """Return dimensions most relevant to the current time period."""
    mapping = {
        "morning": ["spiritual", "physical", "occupational"],
        "deep_work": ["physical", "environmental"],
        "midday": ["social", "physical", "emotional"],
        "afternoon": ["intellectual", "environmental", "occupational"],
        "evening": ["emotional", "spiritual", "social"],
        "wind_down": ["physical", "emotional", "spiritual"],
        "late_night": ["physical"],  # sleep focus
    }
    return mapping.get(period, list(mapping["morning"]))


def get_nudge(data, dimension=None, time_aware=True):
    """Get a single nudge, optionally filtered by dimension and time."""
    dimensions = data["dimensions"]

    if dimension:
        if dimension not in dimensions:
            print(f"Unknown dimension: {dimension}")
            print(f"Available: {', '.join(dimensions.keys())}")
            return None
        dim_data = dimensions[dimension]
        tips = dim_data["tips"]
    else:
        # Pick a time-appropriate dimension
        period = get_time_period()
        if time_aware:
            preferred = get_time_appropriate_dimensions(period)
            dimension = random.choice(preferred)
        else:
            dimension = random.choice(list(dimensions.keys()))
        dim_data = dimensions[dimension]
        tips = dim_data["tips"]

    # Filter by time if possible
    period = get_time_period()
    time_filtered = [t for t in tips if t["time"] == period or t["time"] == "any"]
    if not time_filtered:
        time_filtered = tips

    tip = random.choice(time_filtered)
    return {
        "dimension": dimension,
        "icon": dim_data["icon"],
        "tip": tip,
    }


def format_nudge(nudge):
    """Format a nudge for terminal display."""
    if not nudge:
        return ""
    icon = nudge["icon"]
    dim = nudge["dimension"].capitalize()
    action = nudge["tip"]["action"]
    science = nudge["tip"]["science"]

    lines = [
        "",
        f"  {icon} {dim}",
        f"  {action}",
        "",
        f"  📎 Why: {science}",
        "",
    ]
    return "\n".join(lines)


def late_night_warning():
    """Special message for late-night workers."""
    return """
  🌙 KeepWell: It's past 11 PM.

  Sleep debt accumulates and cannot be "repaid" on weekends.
  Every hour of sleep lost tonight costs you 2 hours of cognitive
  performance tomorrow.

  📎 Why: Sleep deprivation impairs prefrontal cortex function,
  reducing decision-making quality by 50% (Walker, 2017).

  Consider: Save your work and set a fresh start for tomorrow morning.
"""


def weekly_reflection():
    """Print the weekly reflection prompt."""
    return """
  ╭──────────────────────────────────────────────╮
  │        KeepWell Weekly Reflection             │
  ╰──────────────────────────────────────────────╯

  Rate each dimension 1-5 (1 = struggling, 5 = thriving):

  🏃 Physical:      How was your energy and movement?       ___/5
  💭 Emotional:     How was your mood stability?            ___/5
  💼 Occupational:  Did work feel meaningful?               ___/5
  🤝 Social:        Did you feel connected to others?       ___/5
  📖 Intellectual:  Did you learn something new?            ___/5
  🌿 Environmental: Was your workspace comfortable?         ___/5
  💰 Financial:     Any money-related stress?               ___/5
  ✨ Spiritual:     Did you feel aligned with your values?  ___/5

  ─────────────────────────────────────────────────

  Reflection questions:
  • Which dimension scored lowest? What's one micro-step to improve it?
  • Which dimension scored highest? How can you maintain it?
  • What's one thing you'll do differently next week?

"""


def list_dimensions(data):
    """List all 8 dimensions with descriptions."""
    print("\n  KeepWell AI — 8 Dimensions of Wellness\n")
    print("  Based on SAMHSA Wellness Framework\n")
    for dim_name, dim_data in data["dimensions"].items():
        icon = dim_data["icon"]
        count = len(dim_data["tips"])
        print(f"  {icon} {dim_name.capitalize():14s} ({count} tips)")
    total = sum(len(d["tips"]) for d in data["dimensions"].values())
    print(f"\n  Total: {total} evidence-based nudges across 8 dimensions\n")


def main():
    parser = argparse.ArgumentParser(
        description="KeepWell AI — Evidence-based well-being nudges",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python keepwell.py                      # Smart time-aware nudge
  python keepwell.py -d emotional         # Emotional dimension tip
  python keepwell.py --all                # One tip per dimension
  python keepwell.py --weekly-reflection  # Weekly self-assessment
  python keepwell.py --list-dimensions    # Show all dimensions
        """,
    )
    parser.add_argument(
        "-d", "--dimension",
        choices=["physical", "emotional", "occupational", "social",
                 "intellectual", "environmental", "financial", "spiritual"],
        help="Get a tip from a specific dimension",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Get one tip from each dimension",
    )
    parser.add_argument(
        "--weekly-reflection", action="store_true",
        help="Show weekly reflection template",
    )
    parser.add_argument(
        "--list-dimensions", action="store_true",
        help="List all 8 dimensions",
    )
    parser.add_argument(
        "--no-time", action="store_true",
        help="Disable time-aware filtering",
    )
    parser.add_argument(
        "--lang", choices=["en", "zh", "zh-TW"],
        default="en",
        help="Language for tips (en or zh/zh-TW for Traditional Chinese)",
    )

    args = parser.parse_args()
    data = load_tips(args.lang)

    # Late night override
    period = get_time_period()
    if period == "late_night" and not args.dimension and not args.all:
        print(late_night_warning())
        return

    if args.weekly_reflection:
        print(weekly_reflection())
    elif args.list_dimensions:
        list_dimensions(data)
    elif args.all:
        print("\n  KeepWell AI — Today's Wellness Round\n")
        for dim_name in data["dimensions"]:
            nudge = get_nudge(data, dimension=dim_name, time_aware=False)
            if nudge:
                print(format_nudge(nudge))
                print("  ─" * 20)
    else:
        nudge = get_nudge(data, dimension=args.dimension, time_aware=not args.no_time)
        if nudge:
            print(format_nudge(nudge))


if __name__ == "__main__":
    main()
