# 🧠 KeepWell AI

**An evidence-based AI well-being companion for developers and knowledge workers.**

KeepWell AI is a Kiro Skill that delivers context-aware well-being nudges grounded in behavioral science. It covers all 8 dimensions of wellness and adapts to your work rhythm using circadian and ultradian cycles.

---

## Why KeepWell AI?

Most productivity tools treat humans like machines. KeepWell AI treats you like a human who happens to use machines.

- 🕐 **Time-aware** — Different nudges for morning focus, afternoon dip, and evening wind-down
- 🎯 **8 Dimensions** — Physical, Emotional, Occupational, Social, Intellectual, Environmental, Financial, Spiritual
- 📚 **Science-backed** — Every nudge references a behavioral science principle
- 🔄 **Non-repetitive** — Rotates across dimensions so you never get the same tip twice in a row
- ⚙️ **Customizable** — Set your schedule, preferences, and which dimensions matter most to you

---

## Quick Start

### Install as Kiro Steering

Copy the `steering/keepwell.md` file into your project's `.kiro/steering/` folder:

```bash
cp steering/keepwell.md /your-project/.kiro/steering/keepwell.md
```

### Install Hooks (Optional)

Copy the hook files to activate automatic reminders:

```bash
cp hooks/*.json /your-project/.kiro/hooks/
```

### Use as CLI (Standalone)

```bash
python scripts/keepwell.py --dimension physical
python scripts/keepwell.py --time-aware
python scripts/keepwell.py --weekly-reflection
```

---

## 8 Dimensions of Wellness

Based on the [SAMHSA Wellness Framework](https://www.samhsa.gov/wellness):

| Dimension | Focus | Example Nudge |
|-----------|-------|---------------|
| Physical | Movement, sleep, nutrition | "You've been sitting for 90 min. Stand up and do 10 shoulder rolls." |
| Emotional | Self-awareness, stress management | "Name one emotion you're feeling right now. Labeling reduces intensity by 43%." |
| Occupational | Work-life boundaries, purpose | "What's the ONE thing that matters today? Park the rest." |
| Social | Connection, belonging | "Send a 2-sentence message to someone you haven't talked to this week." |
| Intellectual | Learning, curiosity | "Spend 5 minutes reading something unrelated to your current task." |
| Environmental | Workspace, nature | "Look out a window for 20 seconds. Distance gazing relaxes the ciliary muscle." |
| Financial | Security, planning | "Is there one subscription you're paying for but not using?" |
| Spiritual | Purpose, gratitude | "Name one thing you did today that aligns with your values." |

---

## Science Behind It

See [SCIENCE.md](./SCIENCE.md) for the full theoretical framework. Key models:

- **SAMHSA 8 Dimensions of Wellness** — Holistic wellness structure
- **Ultradian Rhythm (Rossi, 1991)** — 90-120 min work/rest cycles
- **Nudge Theory (Thaler & Sunstein, 2008)** — Choice architecture for behavior change
- **Self-Determination Theory (Deci & Ryan, 2000)** — Autonomy, competence, relatedness
- **Transtheoretical Model (Prochaska, 1997)** — Stages of behavior change
- **Affect Labeling (Lieberman et al., 2007)** — Naming emotions reduces amygdala activity
- **Attention Restoration Theory (Kaplan, 1995)** — Nature exposure restores directed attention

---

## Configuration

Edit `steering/keepwell.md` to customize:

```yaml
# Your preferences
wake_time: "07:00"
sleep_time: "23:00"
work_start: "09:00"
work_end: "18:00"
break_interval_minutes: 90
priority_dimensions: [physical, emotional, occupational]
language: "en"  # or "zh-TW" for Traditional Chinese
```

---

## Project Structure

```
keepwell-ai/
├── README.md                  # This file
├── SCIENCE.md                 # Theoretical framework & references
├── LICENSE                    # MIT
├── hooks/                     # Kiro Hook definitions
│   ├── morning-checkin.json
│   ├── break-reminder.json
│   ├── evening-wind-down.json
│   └── weekly-reflection.json
├── steering/
│   └── keepwell.md            # Core AI behavior rules
├── data/
│   └── wellbeing-tips.json    # 8-dimension tip database
└── scripts/
    └── keepwell.py            # CLI tool
```

---

## Who Made This

Created by **Wayne Wang** — 17 years in occupational health, EHS, and well-being program design across HP, Logitech, and AWS. Health Behavior Science trained (NTNU), MHFA certified.

This tool is the AI evolution of programs I've built for 10,000+ employees across APAC: HP's *Keep Well-Being at Work*, Logitech's *Safety Month*, and AWS's *DC Well-being* initiatives.

---

## License

MIT — Use it, fork it, make your team healthier.
