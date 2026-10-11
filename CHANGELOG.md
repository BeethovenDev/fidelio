# Changelog

All notable changes to FIDELIO are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-10-11

### Added

- The **offline OPSEC self-audit**: a questionnaire across eight categories
  (accounts, email, phone, metadata, network & DNS, browser & device, secrets,
  social surface), a per-category 0–100 risk score and a weighted overall
  score.
- `fidelio audit` — interactive walk-through by default, fully scriptable with
  `--answers answers.json` and `--weights weights.json`; `--json` reports
  machine-readable scores.
- `fidelio audit --report roadmap.md` — a remediation roadmap that restates
  each imperfect answer next to the concrete countermeasure.
- `fidelio list-questions` — the full taxonomy in text or `--json`.
- Zero runtime dependencies, Python 3.10+, strict mypy and ruff, pytest suite.