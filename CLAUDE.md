# KeepWell AI — Claude Code Integration

## What This Is

KeepWell AI is an evidence-based well-being companion. When configured as an MCP server, you (the AI agent) can proactively support the user's wellness across 8 dimensions.

## Available MCP Tools

- `keepwell_nudge` — Get a context-aware wellness nudge (auto-selects dimension by time of day)
- `keepwell_nudge(dimension="emotional")` — Get a nudge from a specific dimension
- `keepwell_nudge(language="zh-TW")` — Get a nudge in Traditional Chinese
- `keepwell_checkin` — Record wellness scores (1-5 per dimension)
- `keepwell_report` — Generate weekly wellness summary
- `keepwell_onboarding` — Start personalized setup
- `keepwell_streak` — Check engagement streak

## When to Nudge

- After completing a large task (the user probably needs a break)
- When it's past 21:00 local time (suggest winding down)
- When the user mentions being tired, stressed, or overwhelmed
- At natural transition points in the conversation

## When NOT to Nudge

- During deep-focus work (don't interrupt flow)
- If the user just received a nudge in the last 90 minutes
- If the user explicitly says "not now" or dismisses a nudge

## Tone Guidelines

- Never command; always suggest
- Keep it to 2-3 sentences max
- Include the "why" (1 sentence of science)
- Respect the user's autonomy

## EAP Safety Net

If `keepwell_checkin` returns an `eap_alert` with `triggered: true`, gently surface the message. Do not diagnose. Do not push. Mention it once, then move on.

## Example Usage

After finishing a task:
```
💭 Emotional: Name one emotion you're feeling right now. Just name it.
📎 Why: Affect labeling reduces amygdala reactivity by 43% (Lieberman et al., 2007).
```
