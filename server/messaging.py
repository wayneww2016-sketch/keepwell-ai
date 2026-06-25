#!/usr/bin/env python3
"""
KeepWell AI — Messaging Channels
Supports Slack, Telegram, Microsoft Teams, CLI, and generic webhook.
Zero external dependencies (uses urllib from stdlib).
"""

import json
import urllib.request
import urllib.error
from pathlib import Path


def load_messaging_config():
    """Load messaging config from keepwell.config.json."""
    config_paths = [
        Path.cwd() / "keepwell.config.json",
        Path(__file__).parent.parent / "config" / "keepwell.config.json",
    ]
    for p in config_paths:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("messaging", {})
    return {}


def send_slack(webhook_url, message, icon="🧠", username="KeepWell AI"):
    """Send message to Slack via incoming webhook."""
    payload = {
        "username": username,
        "icon_emoji": icon,
        "text": message,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return {"status": "sent", "channel": "slack", "code": resp.status}
    except urllib.error.HTTPError as e:
        return {"status": "error", "channel": "slack", "code": e.code, "reason": str(e)}


def send_telegram(bot_token, chat_id, message):
    """Send message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return {"status": "sent", "channel": "telegram", "code": resp.status}
    except urllib.error.HTTPError as e:
        return {"status": "error", "channel": "telegram", "code": e.code, "reason": str(e)}


def send_teams(webhook_url, message):
    """Send message to Microsoft Teams via incoming webhook."""
    payload = {"text": message}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(webhook_url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return {"status": "sent", "channel": "teams", "code": resp.status}
    except urllib.error.HTTPError as e:
        return {"status": "error", "channel": "teams", "code": e.code, "reason": str(e)}


def send_webhook(url, message):
    """Send to generic webhook (POST JSON)."""
    payload = {"text": message, "source": "keepwell-ai"}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return {"status": "sent", "channel": "webhook", "code": resp.status}
    except urllib.error.HTTPError as e:
        return {"status": "error", "channel": "webhook", "code": e.code, "reason": str(e)}


def send_cli(message):
    """Print to stdout (default channel)."""
    print(f"\n  [KeepWell] {message}\n")
    return {"status": "sent", "channel": "cli"}


def send_message(message, config=None):
    """
    Route message to configured channel.
    Config should have:
      messaging.channel: "slack" | "telegram" | "teams" | "webhook" | "cli"
      messaging.slack_webhook: "https://hooks.slack.com/services/..."
      messaging.telegram_token: "bot_token"
      messaging.telegram_chat_id: "chat_id"
      messaging.teams_webhook: "https://..."
      messaging.webhook_url: "https://..."
    """
    if config is None:
        config = load_messaging_config()

    channel = config.get("channel", "cli")

    if channel == "slack":
        webhook = config.get("slack_webhook", "")
        if not webhook:
            return {"status": "error", "reason": "slack_webhook not configured"}
        return send_slack(webhook, message)

    elif channel == "telegram":
        token = config.get("telegram_token", "")
        chat_id = config.get("telegram_chat_id", "")
        if not token or not chat_id:
            return {"status": "error", "reason": "telegram_token or telegram_chat_id not configured"}
        return send_telegram(token, chat_id, message)

    elif channel == "teams":
        webhook = config.get("teams_webhook", "")
        if not webhook:
            return {"status": "error", "reason": "teams_webhook not configured"}
        return send_teams(webhook, message)

    elif channel == "webhook":
        url = config.get("webhook_url", "")
        if not url:
            return {"status": "error", "reason": "webhook_url not configured"}
        return send_webhook(url, message)

    else:
        return send_cli(message)


def format_nudge_message(nudge):
    """Format a nudge dict into a readable message string."""
    icon = nudge.get("icon", "🧠")
    dim = nudge.get("dimension", "").capitalize()
    action = nudge.get("action", "")
    science = nudge.get("science", "")
    streak = nudge.get("streak", 0)

    msg = f"{icon} *{dim}*\n{action}\n\n📎 Why: {science}"
    if streak > 1:
        msg += f"\n\n🔥 Streak: {streak} days"
    return msg
