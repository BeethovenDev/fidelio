<div align="center">

# FIDELIO

**An offline OPSEC self-audit — how loud is your digital footprint?**

*Named after Beethoven's only opera: Faithful Love above all — a prisoner held
under a hidden identity, and a study in what a person is willing to protect.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](#philosophy)

</div>

---

FIDELIO scores the habits that together *are* your footprint — accounts, email,
phone, metadata, network & DNS, browser & device, secrets, and your social
surface — and turns the answers into a remediation roadmap. It runs entirely
offline: **no network calls, no telemetry, no stored state** unless you keep a
report you asked for.

It pairs naturally with [EROICA](https://github.com/BeethovenDev/eroica) (which
hardens the browser *itself*): EROICA makes the instrument quiet, FIDELIO makes
the musician disciplined.

> **What this is.** A defensive, self-directed review for investigators,
> journalists and anyone who would rather not leave a trail. **What this is
> not.** A guarantee of anonymity, a detector, or a substitute for a threat
> model. The last line of every report says so.

## Install

```bash
git clone https://github.com/BeethovenDev/fidelio.git
cd fidelio
python -m pip install -e .
```

## Quick start

```bash
# Walk through the questionnaire interactively
fidelio audit

# Non-interactive: pre-baked answers, plus a roadmap file
fidelio audit --answers answers.json --report roadmap.md

# See the whole taxonomy up front
fidelio list-questions
```

`--json` turns any command machine-readable:

```bash
fidelio --json audit --answers answers.json
```

## Scoring

Every answer carries a risk `0..3`. A category score is
`100 · raw / max_raw` — low is disciplined, high is loud. An optional per-
category weight folds into the overall score, so you can emphasize what your
threat model says matters most:

```json
{ "phone": 2.0, "social": 1.5 }
```

## Commands

| Command | Description |
|---------|-------------|
| `fidelio audit` | Run the audit; `--answers` for automation |
| `fidelio audit --report x.md` | Also write a remediation roadmap |
| `fidelio list-questions` | Print the question bank and categories |

## How it works

```
questions/  eight categories × four questions, each answer mapped to risk 0..3
   ▼
core.py     evaluate() → per-category 100·raw/max_raw + weighted overall
   ▼
cli.py      audit (interactive or --answers) → text, --json, or --report .md
```

## Philosophy

* **Teach, don't shame.** The remediation lives in the question itself: every
  item restates what you answered and what to do next.
* **Nothing leaves the machine.** FIDELIO has no network path; answers never
  persist unless *you* keep a report.
* **Scores are habits, not identities.** A perfect score is discipline — it
  never proves anonymity. The report reminds you of that.

## License

MIT