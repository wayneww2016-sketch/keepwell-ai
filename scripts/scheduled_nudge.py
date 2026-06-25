#!/usr/bin/env python3
"""
KeepWell AI — Scheduled Nudge Dispatcher
Run via cron, Windows Task Scheduler, or LaunchAgent.
Sends a well-being nudge to your configured messaging channel.

Usage:
    # Send a time-aware nudge to Slack
    python scheduled_nudge.py

    # Send weather-aware nudge
    python scheduled_nudge.py --weather

    # Send to specific channel (override config)
    python scheduled_nudge.py --channel slack

    # Dry run (print only, don't send)
    python scheduled_nudge.py --dry-run

Scheduling examples:
    # Cron (Linux/Mac): Every 90 minutes during work hours
    */90 9-18 * * 1-5 python3 /path/to/scheduled_nudge.py --weather

    # Windows Task Scheduler: See README for setup guide
"""

import sys
import argparse
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "server"))

from keepwell_server import get_nudge, load_config, get_time_period
from messaging import send_message, format_nudge_message, load_messaging_config
from weather import get_weather, get_weather_nudge


def main():
    parser = argparse.ArgumentParser(description="KeepWell AI Scheduled Nudge")
    parser.add_argument("--weather", action="store_true", help="Include weather-aware nudge")
    parser.add_argument("--channel", type=str, help="Override messaging channel")
    parser.add_argument("--dry-run", action="store_true", help="Print message without sending")
    parser.add_argument("--lang", type=str, default=None, help="Language override")
    parser.add_argument(
        "-d", "--dimension",
        choices=["physical", "emotional", "occupational", "social",
                 "intellectual", "environmental", "financial", "spiritual"],
        help="Specific dimension",
    )
    args = parser.parse_args()

    config = load_config()
    lang = args.lang or config.get("profile", {}).get("language", "en")
    period = get_time_period(config)

    # Respect quiet hours (late_night = don't send)
    if period == "late_night" and not args.dry_run:
        print("  [KeepWell] Quiet hours active. No nudge sent.")
        return

    # Get nudge
    if args.weather:
        # Try weather-aware nudge first
        location = config.get("location", {})
        lat = location.get("latitude", 25.03)  # Default: Taipei
        lon = location.get("longitude", 121.57)
        weather_data = get_weather(lat, lon)

        if weather_data.get("success"):
            weather_nudge = get_weather_nudge(weather_data, lang)
            if weather_nudge:
                message = format_weather_message(weather_nudge, weather_data)
            else:
                # Fallback to regular nudge
                nudge = get_nudge(dimension=args.dimension, lang=lang, config=config)
                message = format_nudge_message(nudge)
        else:
            # Weather unavailable, fallback
            nudge = get_nudge(dimension=args.dimension, lang=lang, config=config)
            message = format_nudge_message(nudge)
    else:
        nudge = get_nudge(dimension=args.dimension, lang=lang, config=config)
        message = format_nudge_message(nudge)

    # Send or print
    if args.dry_run:
        print(f"\n  [DRY RUN] Would send:\n")
        print(f"  {message}\n")
        return

    msg_config = load_messaging_config()
    if args.channel:
        msg_config["channel"] = args.channel

    result = send_message(message, msg_config)
    if result.get("status") == "sent":
        print(f"  ✓ Nudge sent via {result['channel']}")
    else:
        print(f"  ✗ Failed: {result.get('reason', 'unknown error')}")


def format_weather_message(nudge, weather_data):
    """Format weather nudge with weather context."""
    temp = weather_data.get("temperature", "?")
    desc = weather_data.get("weather_desc", "").replace("_", " ")

    msg = f"🌤️ Weather: {temp}°C, {desc}\n\n"
    msg += f"{nudge['icon']} *{nudge['dimension'].capitalize()}*\n"
    msg += nudge["action"]
    msg += f"\n\n📎 Why: {nudge['science']}"

    if nudge.get("uv_warning"):
        msg += f"\n\n⚠️ {nudge['uv_warning']}"

    return msg


if __name__ == "__main__":
    main()
