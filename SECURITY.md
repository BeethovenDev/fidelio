# Security policy

## Scope

FIDELIO is a local, offline tool. It makes **no network calls**, collects
**no telemetry**, and stores **no answers** unless you keep a report you
generated yourself. The code you run is the code you audit.

## Reporting a vulnerability

Please do **not** open a public issue for a security problem. Report it
privately via GitHub's [Security Advisories] for this repository.

- Include the version, platform and Python version.
- Include a minimal reproduction. For report-generation bugs, mark the output
  as containing only mock data before sharing it.
- Do not paste real answer files into any public channel.

Every report is acknowledged within 5 business days.

## Hardening expectations

- No dependency on the network at runtime — the question bank and scoring are
  local assets.
- Report files are written only where you tell FIDELIO to write them; no
  hidden caches.
- If you spot a question whose wording nudges rather than informs, open a
  discussion: the questionnaire is meant to teach, not to shame.

[Security Advisories]: https://github.com/BeethovenDev/fidelio/security/advisories