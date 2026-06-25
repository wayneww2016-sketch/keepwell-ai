#!/usr/bin/env python3
"""
KeepWell AI — MCP Server
Evidence-based well-being companion for knowledge workers.
Implements Model Context Protocol for universal AI IDE compatibility.
"""

import json
import random
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent to path for data access
SERVER_DIR = Path(__file__).parent
PROJECT_DIR = SERVER_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
HISTORY_DIR = PROJECT_DIR / "history"

# Ensure history directory exists
HISTORY_DIR.mkdir(exist_ok=True)


def load_tips(lang="en"):
    """Load tips database."""
    filename = "wellbeing-tips-zh.json" if lang in ("zh", "zh-TW") else "wellbeing-tips.json"
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def load_config():
    """Load user config, falling back to defaults."""
    config_paths = [
        Path.cwd() / "keepwell.config.json",
        PROJECT_DIR / "config" / "keepwell.config.json",
    ]
    for p in config_paths:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return get_default_config()


def get_default_config():
    """Return default configuration."""
    return {
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
        "profile": {"language": "en", "name": ""},
    }


def parse_time(time_str):
    """Parse HH:MM to float hours."""
    h, m = time_str.split(":")
    return int(h) + int(m) / 60


def get_time_period(config=None):
    """Get current time period based on config schedule."""
    if config is None:
        config = get_default_config()
    sched = config["schedule"]
    now = datetime.now().hour + datetime.now().minute / 60

    wake = parse_time(sched["wake_time"])
    work_start = parse_time(sched["work_start"])
    lunch_start = parse_time(sched["lunch_start"])
    lunch_end = parse_time(sched["lunch_end"])
    work_end = parse_time(sched["work_end"])
    sleep = parse_time(sched["sleep_time"])

    if wake > sleep:  # Night shift
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
    else:  # Normal schedule
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


TIME_DIMENSIONS = {
    "morning": ["spiritual", "physical", "occupational"],
    "deep_work": ["physical", "environmental"],
    "midday": ["social", "physical", "emotional"],
    "afternoon": ["intellectual", "environmental", "occupational"],
    "evening": ["emotional", "spiritual", "social"],
    "wind_down": ["physical", "emotional", "spiritual"],
    "late_night": ["physical"],
}


# ─── History & Streak Tracking ───────────────────────────────────

def get_history_file():
    """Get today's history file path."""
    today = datetime.now().strftime("%Y-%m-%d")
    return HISTORY_DIR / f"{today}.json"


def load_today_history():
    """Load today's nudge history."""
    f = get_history_file()
    if f.exists():
        with open(f, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {"date": datetime.now().strftime("%Y-%m-%d"), "nudges": [], "checkins": []}


def save_history(history):
    """Save today's history."""
    f = get_history_file()
    with open(f, "w", encoding="utf-8") as fh:
        json.dump(history, fh, ensure_ascii=False, indent=2)


def record_nudge(dimension, action, responded=False):
    """Record a nudge delivery."""
    history = load_today_history()
    history["nudges"].append({
        "time": datetime.now().strftime("%H:%M"),
        "dimension": dimension,
        "action": action,
        "responded": responded,
    })
    save_history(history)


def record_checkin(scores):
    """Record a wellness check-in."""
    history = load_today_history()
    history["checkins"].append({
        "time": datetime.now().strftime("%H:%M"),
        "scores": scores,
    })
    save_history(history)


def get_streak():
    """Calculate current streak (consecutive days with at least 1 check-in)."""
    streak = 0
    date = datetime.now()
    while True:
        f = HISTORY_DIR / f"{date.strftime('%Y-%m-%d')}.json"
        if f.exists():
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if data.get("checkins") or data.get("nudges"):
                streak += 1
                date -= timedelta(days=1)
            else:
                break
        else:
            break
    return streak


def get_weekly_summary():
    """Get past 7 days of wellness data."""
    summary = []
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        f = HISTORY_DIR / f"{date.strftime('%Y-%m-%d')}.json"
        day_data = {"date": date.strftime("%Y-%m-%d"), "nudges": 0, "checkins": []}
        if f.exists():
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            day_data["nudges"] = len(data.get("nudges", []))
            day_data["checkins"] = data.get("checkins", [])
        summary.append(day_data)
    return summary


# ─── EAP Gateway Logic ───────────────────────────────────────────

def check_eap_threshold(weekly_data):
    """
    Check if emotional scores are consistently low.
    Triggers EAP recommendation if emotional dimension <= 2 for 3+ days.
    Based on JD-R model: persistent low resources signal burnout risk.
    """
    low_emotion_days = 0
    for day in weekly_data:
        for checkin in day.get("checkins", []):
            scores = checkin.get("scores", {})
            if scores.get("emotional", 5) <= 2:
                low_emotion_days += 1
                break

    if low_emotion_days >= 3:
        return {
            "triggered": True,
            "days_low": low_emotion_days,
            "message": (
                "I've noticed your emotional well-being has been low for "
                f"{low_emotion_days} days this week. This is a signal worth paying attention to. "
                "Consider reaching out to your company's Employee Assistance Program (EAP). "
                "EAP services are free, confidential, and available 24/7. "
                "You don't need to be in crisis to use them."
            ),
            "science": (
                "Persistent low emotional resources predict burnout onset within 4-6 weeks "
                "(Bakker & Demerouti, 2007). Early intervention through EAP reduces burnout "
                "progression by 60% (Richmond et al., 1999)."
            ),
        }
    return {"triggered": False}


# ─── Core Nudge Engine ───────────────────────────────────────────

def get_nudge(dimension=None, lang="en", config=None):
    """Get a contextual nudge."""
    if config is None:
        config = load_config()

    data = load_tips(lang)
    dimensions = data["dimensions"]
    period = get_time_period(config)

    # Late night override
    if period == "late_night" and dimension is None:
        return {
            "type": "late_night_warning",
            "icon": "🌙",
            "dimension": "physical",
            "action": "It's past your sleep time. Save your work and wind down.",
            "science": (
                "Sleep debt accumulates and cannot be repaid on weekends. "
                "Every hour lost costs 2 hours of cognitive performance tomorrow (Walker, 2017)."
            ),
            "period": period,
        }

    if dimension:
        if dimension not in dimensions:
            return {"error": f"Unknown dimension: {dimension}. Available: {list(dimensions.keys())}"}
        dim_data = dimensions[dimension]
    else:
        # Smart dimension selection
        preferred = TIME_DIMENSIONS.get(period, ["physical", "emotional"])
        priority = config.get("preferences", {}).get("priority_dimensions", [])
        excluded = config.get("preferences", {}).get("excluded_dimensions", [])

        # Prefer user's priority dimensions that match time
        candidates = [d for d in preferred if d in priority and d not in excluded]
        if not candidates:
            candidates = [d for d in preferred if d not in excluded]
        if not candidates:
            candidates = [d for d in dimensions.keys() if d not in excluded]

        dimension = random.choice(candidates)
        dim_data = dimensions[dimension]

    tips = dim_data["tips"]
    time_filtered = [t for t in tips if t["time"] in (period, "any")]
    if not time_filtered:
        time_filtered = tips

    tip = random.choice(time_filtered)

    # Record the nudge
    record_nudge(dimension, tip["action"])

    return {
        "type": "nudge",
        "icon": dim_data["icon"],
        "dimension": dimension,
        "action": tip["action"],
        "science": tip["science"],
        "intensity": tip["intensity"],
        "period": period,
        "streak": get_streak(),
    }


# ─── Onboarding ─────────────────────────────────────────────────

def generate_onboarding():
    """Generate interactive onboarding questions."""
    return {
        "type": "onboarding",
        "message": "Welcome to KeepWell AI! Let me personalize your experience.",
        "questions": [
            {
                "id": "work_start",
                "question": "What time do you usually start working?",
                "type": "time",
                "default": "09:00",
                "examples": ["07:00", "09:00", "10:30", "20:00 (night shift)"],
            },
            {
                "id": "work_end",
                "question": "What time do you usually stop working?",
                "type": "time",
                "default": "18:00",
                "examples": ["16:00", "18:00", "19:30", "06:00 (night shift)"],
            },
            {
                "id": "sleep_time",
                "question": "What time do you want to be in bed by?",
                "type": "time",
                "default": "23:00",
            },
            {
                "id": "priority_dimensions",
                "question": "Which wellness areas matter most to you? (pick 2-3)",
                "type": "multi_select",
                "options": [
                    {"value": "physical", "label": "🏃 Physical — movement, posture, hydration"},
                    {"value": "emotional", "label": "💭 Emotional — stress, mood, self-awareness"},
                    {"value": "occupational", "label": "💼 Occupational — boundaries, focus, purpose"},
                    {"value": "social", "label": "🤝 Social — connection, belonging"},
                    {"value": "intellectual", "label": "📖 Intellectual — learning, curiosity"},
                    {"value": "environmental", "label": "🌿 Environmental — workspace, nature"},
                    {"value": "financial", "label": "💰 Financial — money stress, planning"},
                    {"value": "spiritual", "label": "✨ Spiritual — purpose, gratitude, values"},
                ],
                "default": ["physical", "emotional", "occupational"],
            },
            {
                "id": "language",
                "question": "Preferred language for nudges?",
                "type": "select",
                "options": [
                    {"value": "en", "label": "English"},
                    {"value": "zh-TW", "label": "繁體中文"},
                ],
                "default": "en",
            },
            {
                "id": "intensity",
                "question": "How often do you want nudges?",
                "type": "select",
                "options": [
                    {"value": "gentle", "label": "Gentle — max 4 per day"},
                    {"value": "moderate", "label": "Moderate — max 8 per day"},
                    {"value": "active", "label": "Active — every 60-90 minutes"},
                ],
                "default": "gentle",
            },
        ],
    }


def save_onboarding(answers):
    """Save onboarding answers as config."""
    config = get_default_config()

    if "work_start" in answers:
        config["schedule"]["work_start"] = answers["work_start"]
    if "work_end" in answers:
        config["schedule"]["work_end"] = answers["work_end"]
    if "sleep_time" in answers:
        config["schedule"]["sleep_time"] = answers["sleep_time"]
    if "priority_dimensions" in answers:
        config["preferences"]["priority_dimensions"] = answers["priority_dimensions"]
    if "language" in answers:
        config["profile"]["language"] = answers["language"]
    if "intensity" in answers:
        intensity_map = {"gentle": 4, "moderate": 8, "active": 12}
        config["preferences"]["nudge_intensity"] = answers["intensity"]
        config["preferences"]["max_nudges_per_day"] = intensity_map.get(answers["intensity"], 8)

    # Save to project config
    config_path = PROJECT_DIR / "config" / "keepwell.config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    return {"status": "saved", "config": config}


# ─── Weekly Report Generator ─────────────────────────────────────

def generate_weekly_report():
    """Generate a weekly wellness report with insights."""
    weekly = get_weekly_summary()
    streak = get_streak()
    eap_check = check_eap_threshold(weekly)

    # Analyze dimension coverage
    all_dims = set()
    total_nudges = 0
    all_scores = {}

    for day in weekly:
        total_nudges += day["nudges"]
        for checkin in day.get("checkins", []):
            for dim, score in checkin.get("scores", {}).items():
                all_dims.add(dim)
                if dim not in all_scores:
                    all_scores[dim] = []
                all_scores[dim].append(score)

    # Calculate averages
    averages = {}
    for dim, scores in all_scores.items():
        averages[dim] = round(sum(scores) / len(scores), 1)

    # Find strongest and weakest
    strongest = max(averages, key=averages.get) if averages else None
    weakest = min(averages, key=averages.get) if averages else None

    # Dimension coverage (how many of 8 were touched)
    coverage = len(all_dims)

    report = {
        "type": "weekly_report",
        "period": {
            "start": (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d"),
            "end": datetime.now().strftime("%Y-%m-%d"),
        },
        "streak": streak,
        "total_nudges": total_nudges,
        "dimension_coverage": f"{coverage}/8",
        "averages": averages,
        "strongest_dimension": strongest,
        "weakest_dimension": weakest,
        "eap_alert": eap_check,
        "insights": [],
    }

    # Generate insights
    if weakest and averages.get(weakest, 5) <= 2.5:
        report["insights"].append(
            f"Your {weakest} dimension averaged {averages[weakest]}/5 this week. "
            f"Consider focusing one micro-action on this area daily."
        )
    if streak >= 7:
        report["insights"].append(
            f"🔥 {streak}-day streak! Consistency is the strongest predictor of behavior change (Lally et al., 2010)."
        )
    if coverage < 4:
        report["insights"].append(
            f"You only engaged {coverage}/8 dimensions this week. "
            "Try adding one nudge from an unfamiliar dimension tomorrow."
        )
    if total_nudges == 0:
        report["insights"].append(
            "No nudges recorded this week. Start small: respond to just one nudge tomorrow."
        )

    return report


# ─── MCP Server Protocol ─────────────────────────────────────────

def handle_request(request):
    """Handle incoming MCP tool calls."""
    method = request.get("method", "")
    params = request.get("params", {})

    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "keepwell_nudge",
                    "description": "Get a context-aware well-being nudge based on time of day and user preferences. Covers 8 dimensions of wellness with science-backed tips.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "dimension": {
                                "type": "string",
                                "enum": ["physical", "emotional", "occupational", "social", "intellectual", "environmental", "financial", "spiritual"],
                                "description": "Specific dimension to get a nudge from. If omitted, auto-selects based on time of day.",
                            },
                            "language": {
                                "type": "string",
                                "enum": ["en", "zh-TW"],
                                "description": "Language for the nudge. Default: en",
                            },
                        },
                    },
                },
                {
                    "name": "keepwell_checkin",
                    "description": "Record a wellness check-in with scores for each dimension (1-5). Tracks history for weekly reports and EAP threshold monitoring.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "physical": {"type": "integer", "minimum": 1, "maximum": 5},
                            "emotional": {"type": "integer", "minimum": 1, "maximum": 5},
                            "occupational": {"type": "integer", "minimum": 1, "maximum": 5},
                            "social": {"type": "integer", "minimum": 1, "maximum": 5},
                            "intellectual": {"type": "integer", "minimum": 1, "maximum": 5},
                            "environmental": {"type": "integer", "minimum": 1, "maximum": 5},
                            "financial": {"type": "integer", "minimum": 1, "maximum": 5},
                            "spiritual": {"type": "integer", "minimum": 1, "maximum": 5},
                        },
                    },
                },
                {
                    "name": "keepwell_report",
                    "description": "Generate a weekly wellness report with streaks, dimension averages, coverage analysis, and EAP alerts.",
                    "inputSchema": {"type": "object", "properties": {}},
                },
                {
                    "name": "keepwell_onboarding",
                    "description": "Start the onboarding process to personalize KeepWell AI settings.",
                    "inputSchema": {"type": "object", "properties": {}},
                },
                {
                    "name": "keepwell_setup",
                    "description": "Save onboarding answers and generate personalized config.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "work_start": {"type": "string", "description": "Work start time (HH:MM)"},
                            "work_end": {"type": "string", "description": "Work end time (HH:MM)"},
                            "sleep_time": {"type": "string", "description": "Target sleep time (HH:MM)"},
                            "priority_dimensions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "2-3 priority wellness dimensions",
                            },
                            "language": {"type": "string", "enum": ["en", "zh-TW"]},
                            "intensity": {"type": "string", "enum": ["gentle", "moderate", "active"]},
                        },
                    },
                },
                {
                    "name": "keepwell_streak",
                    "description": "Get current streak and today's nudge history.",
                    "inputSchema": {"type": "object", "properties": {}},
                },
            ]
        }

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name == "keepwell_nudge":
            config = load_config()
            lang = arguments.get("language", config.get("profile", {}).get("language", "en"))
            result = get_nudge(
                dimension=arguments.get("dimension"),
                lang=lang,
                config=config,
            )
            return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]}

        elif tool_name == "keepwell_checkin":
            scores = {k: v for k, v in arguments.items() if k in [
                "physical", "emotional", "occupational", "social",
                "intellectual", "environmental", "financial", "spiritual"
            ]}
            record_checkin(scores)
            # Check EAP threshold
            weekly = get_weekly_summary()
            eap = check_eap_threshold(weekly)
            result = {
                "status": "recorded",
                "scores": scores,
                "streak": get_streak(),
                "eap_alert": eap,
            }
            return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]}

        elif tool_name == "keepwell_report":
            result = generate_weekly_report()
            return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]}

        elif tool_name == "keepwell_onboarding":
            result = generate_onboarding()
            return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]}

        elif tool_name == "keepwell_setup":
            result = save_onboarding(arguments)
            return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]}

        elif tool_name == "keepwell_streak":
            history = load_today_history()
            result = {
                "streak": get_streak(),
                "today_nudges": len(history.get("nudges", [])),
                "today_checkins": len(history.get("checkins", [])),
            }
            return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]}

        else:
            return {"error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}

    return {"error": {"code": -32601, "message": f"Unknown method: {method}"}}


# ─── Stdio Transport ─────────────────────────────────────────────

def main():
    """Run MCP server over stdio."""
    import sys

    # Read JSON-RPC messages from stdin
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            response["jsonrpc"] = "2.0"
            response["id"] = request.get("id")
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            error_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"},
            }
            sys.stdout.write(json.dumps(error_resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            error_resp = {
                "jsonrpc": "2.0",
                "id": request.get("id") if "request" in dir() else None,
                "error": {"code": -32603, "message": str(e)},
            }
            sys.stdout.write(json.dumps(error_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
