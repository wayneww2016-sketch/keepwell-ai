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


DEFAULT_CONFIG = {
    "schedule": {
        "wake_time": "07:00",
        "sleep_time": "23:00",
        "work_start": "09:00",
        "work_end": "18:00",
        "lunch_start": "12:00",
        "lunch_end": "13:00",
    },
    "preferences": {
        "break_interval_minutes": 90,
        "priority_dimensions": ["physical", "emotional", "occupational"],
        "excluded_dimensions": [],
        "nudge_intensity": "gentle",
        "max_nudges_per_day": 8,
    },
    "profile": {
        "language": "en",
    },
}


def load_config(config_path=None):
    """Load user config, falling back to defaults."""
    config = DEFAULT_CONFIG.copy()

    # Search order: explicit path > ./keepwell.config.json > ../config/keepwell.config.json
    search_paths = []
    if config_path:
        search_paths.append(Path(config_path))
    search_paths.append(Path.cwd() / "keepwell.config.json")
    search_paths.append(Path(__file__).parent.parent / "config" / "keepwell.config.json")

    for p in search_paths:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            # Merge user config into defaults
            for section in user_config:
                if section.startswith("_"):
                    continue
                if section in config and isinstance(config[section], dict):
                    config[section].update(user_config[section])
                else:
                    config[section] = user_config[section]
            break

    return config


def load_tips(lang="en"):
    """Load the wellbeing tips database."""
    if lang == "zh" or lang == "zh-TW":
        filename = "wellbeing-tips-zh.json"
    else:
        filename = "wellbeing-tips.json"
    data_path = Path(__file__).parent.parent / "data" / filename
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_time(time_str):
    """Parse HH:MM string to hour float."""
    parts = time_str.split(":")
    return int(parts[0]) + int(parts[1]) / 60


def get_time_period(config=None):
    """Determine current time period based on user's schedule config."""
    if config is None:
        config = DEFAULT_CONFIG

    sched = config["schedule"]
    now = datetime.now().hour + datetime.now().minute / 60

    wake = parse_time(sched["wake_time"])
    work_start = parse_time(sched["work_start"])
    lunch_start = parse_time(sched["lunch_start"])
    lunch_end = parse_time(sched["lunch_end"])
    work_end = parse_time(sched["work_end"])
    sleep = parse_time(sched["sleep_time"])

    # Handle overnight schedules (night shift)
    if wake > sleep:
        # Night shift: sleep time is "morning" for them
        if now >= sleep and now < wake:
            return "late_night"
        elif now >= wake and now < wake + 2:
            return "morning"
        elif now >= work_start and now < lunch_start:
            return "deep_work"
        elif now >= lunch_start and now < lunch_end:
            return "midday"
        elif now >= lunch_end and now < work_end:
            return "afternoon"
        elif now >= work_end and now < sleep:
            return "evening"
        else:
            return "wind_down"
    else:
        # Normal schedule
        if now < wake or now >= sleep:
            return "late_night"
        elif now >= wake and now < work_start:
            return "morning"
        elif now >= work_start and now < lunch_start:
            return "deep_work"
        elif now >= lunch_start and now < lunch_end:
            return "midday"
        elif now >= lunch_end and now < work_end:
            return "afternoon"
        elif now >= work_end and now < sleep - 2:
            return "evening"
        else:
            return "wind_down"


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


def get_nudge(data, dimension=None, time_aware=True, config=None):
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
        period = get_time_period(config)
        if time_aware:
            preferred = get_time_appropriate_dimensions(period)
            # Filter by user's priority dimensions if set
            if config and config.get("preferences", {}).get("priority_dimensions"):
                priority = config["preferences"]["priority_dimensions"]
                preferred_filtered = [d for d in preferred if d in priority]
                if preferred_filtered:
                    preferred = preferred_filtered
            dimension = random.choice(preferred)
        else:
            dimension = random.choice(list(dimensions.keys()))
        dim_data = dimensions[dimension]
        tips = dim_data["tips"]

    # Filter by time if possible
    period = get_time_period(config)
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
        default=None,
        help="Language for tips (en or zh/zh-TW for Traditional Chinese)",
    )
    parser.add_argument(
        "--config", type=str, default=None,
        help="Path to custom keepwell.config.json",
    )
    parser.add_argument(
        "--preset", type=str, default=None,
        choices=["early-bird", "night-owl", "shift-worker-night", "remote-flexible"],
        help="Use a built-in preset configuration",
    )
    parser.add_argument(
        "--init", action="store_true",
        help="Create a keepwell.config.json in the current directory",
    )

    args = parser.parse_args()

    # Handle --init
    if args.init:
        import shutil
        src = Path(__file__).parent.parent / "config" / "keepwell.config.json"
        dst = Path.cwd() / "keepwell.config.json"
        if dst.exists():
            print(f"  Config already exists: {dst}")
        else:
            shutil.copy(src, dst)
            print(f"  ✓ Created: {dst}")
            print(f"  Edit this file to customize your schedule and preferences.")
        return

    # Load config
    config_path = args.config
    if args.preset:
        config_path = str(Path(__file__).parent.parent / "config" / "presets" / f"{args.preset}.json")
    config = load_config(config_path)

    # Determine language
    lang = args.lang or config.get("profile", {}).get("language", "en")
    data = load_tips(lang)

    # Late night override
    period = get_time_period(config)
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
            nudge = get_nudge(data, dimension=dim_name, time_aware=False, config=config)
            if nudge:
                print(format_nudge(nudge))
                print("  ─" * 20)
    else:
        nudge = get_nudge(data, dimension=args.dimension, time_aware=not args.no_time, config=config)
        if nudge:
            print(format_nudge(nudge))


if __name__ == "__main__":
    main()
