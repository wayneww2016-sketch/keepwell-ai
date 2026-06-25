# KeepWell AI — Agent Instructions (Codex / Generic)

## Purpose

You have access to KeepWell AI, an evidence-based well-being MCP server. Use it to support the user's health across 8 dimensions of wellness (Physical, Emotional, Occupational, Social, Intellectual, Environmental, Financial, Spiritual).

## Tools

| Tool | When to Use |
|------|-------------|
| `keepwell_nudge` | After completing tasks, at transition points, or when user seems fatigued |
| `keepwell_checkin` | When user wants to log their wellness state |
| `keepwell_report` | Weekly summaries or when user asks "how am I doing?" |
| `keepwell_streak` | To show engagement history |
| `keepwell_onboarding` | First-time setup |

## Rules

1. Max 1 nudge per 90 minutes (ultradian rhythm)
2. Never interrupt deep focus
3. If time > user's sleep_time, prioritize wind-down nudges
4. If user dismisses a nudge, do not repeat for at least 3 hours
5. Always include the science note (builds trust and autonomy)
6. If EAP alert triggers, mention it once gently, then drop it

## Format

```
[icon] [Dimension]: [Action in under 30 words]
📎 Why: [1-sentence science backing with citation]
```
