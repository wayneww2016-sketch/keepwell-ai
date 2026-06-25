<p align="center">
  <h1 align="center">🧠 KeepWell AI</h1>
  <p align="center">
    <strong>Evidence-based AI well-being companion for knowledge workers</strong>
  </p>
  <p align="center">
    <a href="#quick-start">Quick Start</a> •
    <a href="#features">Features</a> •
    <a href="#science">Science</a> •
    <a href="#configuration">Configuration</a> •
    <a href="#mcp-server">MCP Server</a> •
    <a href="#roadmap">Roadmap</a>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/dimensions-8-76b900" alt="8 Dimensions" />
    <img src="https://img.shields.io/badge/tips-88-5b9bd5" alt="88 Tips" />
    <img src="https://img.shields.io/badge/languages-EN%20%7C%20繁中-4ab4c4" alt="Bilingual" />
    <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License" />
    <img src="https://img.shields.io/badge/science--backed-10%20theories-a78bfa" alt="10 Theories" />
  </p>
</p>

---

Most productivity tools treat humans like machines. KeepWell AI treats you like a human who happens to use machines.

Unlike break-reminder apps that only tell you to "drink water," KeepWell AI delivers **context-aware nudges across all 8 dimensions of wellness**, adapts to your personal schedule (including night shifts), and backs every suggestion with peer-reviewed behavioral science.

---

## Features

| Feature | Description |
|---------|-------------|
| 🎯 **8 Dimensions** | Physical, Emotional, Occupational, Social, Intellectual, Environmental, Financial, Spiritual |
| 🕐 **Time-Aware** | Adapts nudges to morning focus, afternoon dip, evening wind-down |
| 📚 **Science-Backed** | Every tip cites a specific research paper |
| ⚙️ **Personalized** | Config system with presets for different work styles |
| 🌙 **Shift Worker Ready** | Night shift, rotating schedules, DC operators |
| 🌐 **Bilingual** | English + Traditional Chinese (繁體中文) |
| 🔥 **Streak Tracking** | Daily engagement history with weekly reports |
| 📊 **HTML Reports** | Visual weekly wellness dashboard |
| 🚨 **EAP Gateway** | Auto-detects sustained low mood; suggests professional help |
| 🔌 **MCP Server** | Works with any AI IDE (Kiro, Cursor, Claude Code) |
| 🪝 **Kiro Hooks** | Auto-triggers for morning, breaks, and evening |

---

## Quick Start

### Option A: CLI (Standalone)

```bash
git clone https://github.com/wayneww2016-sketch/keepwell-ai.git
cd keepwell-ai

# Get a time-aware nudge
python scripts/keepwell.py

# Chinese nudge
python scripts/keepwell.py --lang zh

# Specific dimension
python scripts/keepwell.py -d emotional

# Weekly reflection
python scripts/keepwell.py --weekly-reflection

# Generate visual report
python scripts/generate_report.py --open
```

### Option B: Kiro Steering + Hooks

```bash
# Copy steering file (AI behavior rules)
cp steering/keepwell.md /your-project/.kiro/steering/

# Copy hooks for auto-reminders
cp hooks/*.json /your-project/.kiro/hooks/
```

### Option B2: Claude Code (CLAUDE.md)

Add this to your project's `CLAUDE.md`:

```markdown
## Well-Being

You have access to the KeepWell AI MCP server. Use it to:
- Call `keepwell_nudge` when the user has been working for a while
- Call `keepwell_checkin` when the user mentions stress or fatigue
- Respect quiet hours: if the time is past the user's configured sleep_time, suggest winding down
- If emotional scores are low for 3+ days, surface the EAP recommendation
```

### Option C: MCP Server (Any AI IDE)

Works with **Kiro**, **Claude Code**, **Cursor**, **Windsurf**, **Codex**, and any MCP-compatible client.

**Kiro** — add to `.kiro/settings/mcp.json`:
```json
{
  "mcpServers": {
    "keepwell-ai": {
      "command": "python",
      "args": ["path/to/keepwell-ai/server/keepwell_server.py"]
    }
  }
}
```

**Claude Code** — add to `.claude/settings.json` or project `CLAUDE.md`:
```json
{
  "mcpServers": {
    "keepwell-ai": {
      "command": "python3",
      "args": ["/absolute/path/to/keepwell-ai/server/keepwell_server.py"]
    }
  }
}
```

**Cursor** — add to `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "keepwell-ai": {
      "command": "python3",
      "args": ["/absolute/path/to/keepwell-ai/server/keepwell_server.py"]
    }
  }
}
```

**Codex CLI** — add to your agent instructions or `.codex/config.json`:
```json
{
  "mcpServers": {
    "keepwell-ai": {
      "command": "python3",
      "args": ["/absolute/path/to/keepwell-ai/server/keepwell_server.py"]
    }
  }
}
```

**Any MCP client** — point to `server/keepwell_server.py` via stdio transport.

### First Run: Onboarding

```bash
# Interactive setup (generates your personal config)
python scripts/keepwell.py --init
```

Or via MCP: call `keepwell_onboarding` to get personalized setup questions.

---

## 8 Dimensions of Wellness

Based on the [SAMHSA Wellness Framework](https://www.samhsa.gov/wellness):

| Dimension | Focus | Example Nudge |
|-----------|-------|---------------|
| 🏃 Physical | Movement, sleep, nutrition | "Stand up and do 10 shoulder rolls." |
| 💭 Emotional | Self-awareness, stress | "Name one emotion you're feeling. Labeling reduces intensity by 43%." |
| 💼 Occupational | Boundaries, purpose | "What's the ONE thing that matters today?" |
| 🤝 Social | Connection, belonging | "Send a 2-sentence appreciation message to a colleague." |
| 📖 Intellectual | Learning, curiosity | "Spend 5 min reading something unrelated to your task." |
| 🌿 Environmental | Workspace, nature | "Look out a window for 20s. Distance gazing relaxes the ciliary muscle." |
| 💰 Financial | Security, planning | "Any subscription you pay for but haven't used in 30 days?" |
| ✨ Spiritual | Purpose, gratitude | "Name one thing you did today that aligns with your values." |

---

## Science

Every design decision is grounded in peer-reviewed research. See [SCIENCE.md](./SCIENCE.md) for the full framework.

| Theory | Application |
|--------|-------------|
| SAMHSA 8 Dimensions | Holistic wellness structure |
| Ultradian Rhythm (Rossi, 1991) | 90-min work/rest cycles |
| Nudge Theory (Thaler & Sunstein, 2008) | Choice architecture |
| Self-Determination Theory (Deci & Ryan, 2000) | Autonomy, not commands |
| Transtheoretical Model (Prochaska, 1997) | Progressive behavior change |
| Affect Labeling (Lieberman et al., 2007) | Naming emotions = regulation |
| Attention Restoration (Kaplan, 1995) | Nature micro-breaks |
| JD-R Model (Bakker & Demerouti, 2007) | Resource-demand balance |
| Two-Process Sleep Model (Borbely, 1982) | Sleep hygiene timing |
| Circadian Chronobiology (Walker, 2017) | Time-of-day optimization |

---

## Configuration

### Quick Setup

```bash
python scripts/keepwell.py --init
# Edit the generated keepwell.config.json
```

### Presets

```bash
python scripts/keepwell.py --preset early-bird          # 5:30 AM riser
python scripts/keepwell.py --preset night-owl           # Late worker
python scripts/keepwell.py --preset shift-worker-night  # Night shift
python scripts/keepwell.py --preset remote-flexible     # WFH flex
```

| Preset | Wake | Work | Sleep | Best For |
|--------|------|------|-------|----------|
| `early-bird` | 05:30 | 07:00-16:00 | 22:00 | Morning people |
| `night-owl` | 09:00 | 10:30-19:30 | 01:00 | Late starters |
| `shift-worker-night` | 18:00 | 20:00-06:00 | 09:00 | DC ops, factory, healthcare |
| `remote-flexible` | 08:00 | 09:00-18:00 | 23:30 | WFH with flex |

### Custom Config

```json
{
  "schedule": {
    "wake_time": "07:00",
    "sleep_time": "23:00",
    "work_start": "09:00",
    "work_end": "18:00"
  },
  "preferences": {
    "break_interval_minutes": 90,
    "priority_dimensions": ["physical", "emotional"],
    "nudge_intensity": "gentle"
  },
  "profile": {
    "language": "zh-TW"
  }
}
```

---

## MCP Server

KeepWell AI runs as an MCP (Model Context Protocol) server, making it compatible with any AI IDE.

### Available Tools

| Tool | Description |
|------|-------------|
| `keepwell_nudge` | Get a context-aware nudge (optional: dimension, language) |
| `keepwell_checkin` | Record dimension scores (1-5) for tracking |
| `keepwell_report` | Generate weekly wellness report |
| `keepwell_onboarding` | Start personalized setup |
| `keepwell_setup` | Save onboarding answers |
| `keepwell_streak` | Get current streak and daily stats |

### EAP Gateway

When emotional dimension scores remain at 2/5 or below for 3+ consecutive days, KeepWell AI surfaces a gentle recommendation to contact the Employee Assistance Program. This is based on the JD-R model finding that persistent low resources predict burnout onset within 4-6 weeks.

The recommendation is:
- Non-diagnostic (never labels the user)
- Informational (explains what EAP is)
- Permission-giving ("You don't need to be in crisis to use them")
- One-time per week (doesn't nag)

---

## Weekly Reports

Generate a visual HTML report:

```bash
python scripts/generate_report.py --open
```

The report includes:
- Total nudges and check-ins
- Dimension score bars (radar-style)
- 7-day activity heatmap
- Streak counter
- EAP alerts (if triggered)

---

## For Teams

> Coming in v2.0

KeepWell AI is designed to scale from individual to team to organization:

### Individual (v1.0 — current)
- Personal config and history
- Self-directed nudges
- Private weekly reports

### Team Lead (v2.0 — planned)
- Deploy config presets across team
- Anonymous aggregated wellness trends
- Identify team-wide burnout signals
- Never surfaces individual data to managers

### Organization (v3.0 — vision)
- EAP integration (auto-surface vendor resources)
- Benefits utilization nudges
- Shift worker schedule sync
- Multi-language deployment across APAC
- Dashboard for People/Well-being teams

---

## Roadmap

- [x] 8-dimension tip database (EN + ZH)
- [x] Time-aware nudge engine
- [x] Personalized config with presets
- [x] Shift worker support
- [x] Streak tracking + history
- [x] Weekly HTML reports
- [x] EAP threshold detection
- [x] MCP Server protocol
- [x] Kiro Hooks integration
- [ ] Slack/Teams bot integration
- [ ] Team-level anonymous aggregation
- [ ] Wearable data integration (sleep, HRV)
- [ ] CBT-lite conversation mode
- [ ] Multi-org deployment (APAC localization)
- [ ] Benefits utilization nudges
- [ ] Manager pulse dashboard (no individual data)

---

## How It's Different

### vs. Break Reminder Extensions (VS Code)

| Feature | Break Reminders | KeepWell AI |
|---------|----------------|-------------|
| Dimensions covered | 1 (Physical) | **8** |
| Scientific backing | None | **10 theories, 44+ citations** |
| Schedule awareness | Fixed timer | **Circadian + ultradian** |
| Shift worker support | No | **Yes** |
| Language | English | **EN + 繁中** |
| Tracking | None | **Streaks, history, reports** |
| Mental health safety net | None | **EAP gateway** |
| Works in AI IDEs | No | **MCP Server** |

### vs. Agent Wellbeing Kit

| Aspect | Agent Wellbeing Kit | KeepWell AI |
|--------|-------------------|-------------|
| **Core problem** | "AI output overwhelms me" | "Knowledge workers neglect well-being" |
| **Approach** | Boundary-setting for agent noise | Proactive wellness intervention |
| **Theory basis** | Experience-based | **10 behavioral science models** |
| **Wellness scope** | Sleep/routine only | **8 SAMHSA dimensions** |
| **EAP integration** | None | **Auto-detect sustained low mood** |
| **Shift workers** | Not supported | **Night shift preset** |
| **Protocol** | Standalone scripts + cron | **MCP Server (universal)** |
| **Multi-language** | English only | **EN + Traditional Chinese** |
| **Target user** | AI power users | **Any knowledge worker + enterprise** |
| **Author expertise** | Developer/indie maker | **17-year well-being professional** |

**Key insight:** Agent Wellbeing Kit solves "my AI is too noisy." KeepWell AI solves "I'm neglecting my health while working." Different problems, different audiences. KeepWell AI is designed for enterprise well-being programs (EAP gateway, shift worker support, multi-language) while remaining useful for individuals.

---

## Project Structure

```
keepwell-ai/
├── README.md                      # This file
├── SCIENCE.md                     # Theoretical framework (10 theories)
├── LICENSE                        # MIT
├── config/
│   ├── keepwell.config.json       # Default config (user copies this)
│   └── presets/                   # Built-in schedule presets
│       ├── early-bird.json
│       ├── night-owl.json
│       ├── shift-worker-night.json
│       └── remote-flexible.json
├── data/
│   ├── wellbeing-tips.json        # 44 English tips
│   └── wellbeing-tips-zh.json     # 44 Chinese tips
├── hooks/                         # Kiro Hook definitions
│   ├── morning-checkin.json
│   ├── break-reminder.json
│   ├── evening-wind-down.json
│   └── weekly-reflection.json
├── server/
│   └── keepwell_server.py         # MCP Server (universal IDE support)
├── scripts/
│   ├── keepwell.py                # CLI tool
│   └── generate_report.py         # HTML report generator
├── steering/
│   └── keepwell.md                # Kiro Steering file
├── history/                       # Auto-generated usage data (gitignored)
└── reports/                       # Auto-generated HTML reports (gitignored)
```

---

## Who Made This

Created by **Wayne Wang** — 17 years in occupational health, EHS, and well-being program design across HP, Logitech, and Amazon Web Services.

- Health Behavior Science trained (National Taiwan Normal University)
- MHFA (Mental Health First Aid) certified
- MBA in Business Analytics (University of Illinois)
- Programs built for 10,000+ employees across 13 APAC countries

This tool is the AI evolution of real programs: HP's *Keep Well-Being at Work*, Logitech's *Safety Month*, and AWS's *DC Well-being* initiatives.

---

## Contributing

Issues and PRs welcome. If you're a well-being professional with evidence-based tips to add, please include the citation.

## License

MIT — Use it, fork it, make your team healthier.
