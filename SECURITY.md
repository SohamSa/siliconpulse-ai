# Security Policy — SiliconPulse AI

## Supported versions

This project is under active construction. Security hardening lands primarily in Phase 16; baseline practices apply from Phase 1.

## Reporting a vulnerability

Do not open a public issue for sensitive reports.

1. Contact the repository maintainers privately (GitHub Security Advisories when the remote is published).
2. Include reproduction steps, impact, and affected components.
3. Allow reasonable time for remediation before disclosure.

## Security baseline (target)

| Control | Status |
| --- | --- |
| `.env.example` without real secrets; `.env` gitignored | Phase 1 done |
| Input validation (Pydantic) | Phase 5+ |
| Parameterized SQL (SQLAlchemy) | Phase 5+ |
| Password hashing + JWT/session auth | Phase 5+ |
| RBAC enforced in API | Phase 5+ |
| Rate limiting, CORS, security headers | Phase 5–16 |
| Agent tool allowlists + approvals | Phase 13 |
| LLM prompt-injection boundaries | Phase 12 |
| Dependabot configuration | Phase 16 |
| Trivy container/dependency scanning | Phase 16 |
| Audit logs for auth and agent actions | Phase 5–13 |

## Secrets

- Never commit API keys, passwords, or certificates.
- Demo credentials in `.env.example` are **development-only** and must be replaced outside local demos.
- Rotate any credential that is accidentally committed.

## Agent and LLM boundaries

- Agents cannot execute arbitrary shell or edit source code.
- High-impact simulated actions require human approval records.
- Copilot must not invent telemetry or execute mutations.
- Healthcare outputs must retain non-diagnostic disclaimers.

## Dependency and image scanning

Trivy and Dependabot configurations will be added under `.github/` and `infrastructure/` in Phase 16. Until then, prefer pinned versions in manifests and review dependency additions for purpose.

## Healthcare module

The healthcare simulation is **not** a medical device or diagnostic system. It must not be connected to real patient-care workflows.
