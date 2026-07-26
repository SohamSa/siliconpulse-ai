# Contributing to SiliconPulse AI

Thank you for helping build a coherent, local-first hardware intelligence platform.

## Principles

1. **Product first** — every dependency must solve a clear product problem.
2. **Phase discipline** — complete phase exit criteria before expanding scope.
3. **No placeholders for “done” features** — runnable and tested, or not claimed done.
4. **Honest limitations** — never claim real semiconductor or medical validation.
5. **Human-in-the-loop** — high-impact agent actions require approval.

## Development setup (Phase 1)

Prerequisites:

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)
- Node.js 20+
- Docker Desktop (required from Phase 2)

```bash
cp .env.example .env
make setup
# Windows PowerShell alternative:
# ./scripts/setup/Setup.ps1
```

## Workflow

1. Inspect relevant files and tests before changing code.
2. Prefer small, coherent changes; reuse `packages/shared-*` models.
3. Add tests, logs, and typed interfaces with features.
4. Run `make lint` and `make test` for affected areas.
5. Update docs when behavior or architecture changes.
6. Do not commit secrets or `.env`.

## Code standards

### Python

- Ruff + mypy (strict as configured)
- Type hints on public interfaces
- Structured logging; no silent exception swallowing

### TypeScript

- `strict` mode; avoid unrestricted `any`
- ESLint + Prettier
- Loading / empty / error UI states for product surfaces

## Testing

- Unit tests under `tests/unit`
- Integration tests under `tests/integration` (Compose-dependent)
- E2E Playwright under `tests/end-to-end` (Phase 16)
- Do not claim tests passed unless executed

## Pull requests

- Describe phase / feature and acceptance checks
- Link checklist items in `IMPLEMENTATION_CHECKLIST.md`
- Include verification steps and known limitations

## Non-negotiables

See master product rules: Redpanda telemetry path, no LLM inventing diagnoses, no hidden scenario labels in RCA, no unrestricted agents, no paid-service hard dependencies for core paths.
