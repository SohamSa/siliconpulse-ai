# SiliconPulse AI — developer commands
# Prefer: make <target>

SHELL := /bin/sh
.DEFAULT_GOAL := help
COMPOSE := docker compose
COMPOSE_FILES := -f docker-compose.yml

.PHONY: help setup up down logs ps migrate seed test lint format typecheck demo reset train-models sync-python sync-web compose-validate wait-healthy

help: ## Show available targets
	@echo "SiliconPulse AI Make targets"
	@echo ""
	@echo "  setup            Install local tooling dependencies (uv + npm)"
	@echo "  up               Start Docker Compose infrastructure"
	@echo "  down             Stop Docker Compose stack"
	@echo "  logs             Tail Compose logs"
	@echo "  ps               Show Compose service status"
	@echo "  wait-healthy     Wait until core infra healthchecks pass"
	@echo "  migrate          Run Alembic migrations (Phase 5+)"
	@echo "  seed             Seed demo data (Phase 5+)"
	@echo "  test             Run unit tests"
	@echo "  lint             Run Ruff + frontend ESLint"
	@echo "  format           Auto-format Python and frontend"
	@echo "  typecheck        Run mypy + TypeScript checks"
	@echo "  demo             Run cooling-failure demo script (Phase 17)"
	@echo "  reset            Reset local simulation / volatile state (Phase 3+)"
	@echo "  train-models     Train ML models (Phase 8+)"
	@echo "  sync-python      uv sync workspace"
	@echo "  sync-web         npm install in apps/web"
	@echo "  compose-validate Validate docker-compose.yml"

setup: sync-python sync-web ## Install dependencies
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example"; fi
	@echo "Setup complete. Start infra with: make up"

sync-python: ## Sync Python workspace with uv
	@command -v uv >/dev/null 2>&1 || { echo "ERROR: uv is not installed. See https://github.com/astral-sh/uv"; exit 1; }
	uv sync --all-packages --group dev

sync-web: ## Install frontend dependencies
	@command -v npm >/dev/null 2>&1 || { echo "ERROR: npm is not installed."; exit 1; }
	cd apps/web && npm install

up: ## Start infrastructure stack
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example"; fi
	$(COMPOSE) $(COMPOSE_FILES) up -d
	@$(MAKE) wait-healthy
	@echo ""
	@echo "Infrastructure is up:"
	@echo "  Postgres:          localhost:$${POSTGRES_PORT:-5432}"
	@echo "  Valkey:            localhost:$${VALKEY_PORT:-6379}"
	@echo "  Redpanda Kafka:    localhost:19092"
	@echo "  Redpanda Console:  http://localhost:$${REDPANDA_CONSOLE_PORT:-8080}"
	@echo "  MinIO API:         http://localhost:9000"
	@echo "  MinIO Console:     http://localhost:9001"
	@echo "  Prometheus:        http://localhost:$${PROMETHEUS_PORT:-9090}"
	@echo "  Grafana:           http://localhost:$${GRAFANA_PORT:-3001}"

down: ## Stop stack (keeps volumes)
	$(COMPOSE) $(COMPOSE_FILES) down

logs: ## Tail logs
	$(COMPOSE) $(COMPOSE_FILES) logs -f

ps: ## Service status
	$(COMPOSE) $(COMPOSE_FILES) ps

wait-healthy: ## Wait for healthy / completed init jobs
	@echo "Waiting for infrastructure health..."
	@i=1; \
	while [ $$i -le 90 ]; do \
	  unhealthy=$$($(COMPOSE) $(COMPOSE_FILES) ps --format json 2>/dev/null | grep -c '"Health":"unhealthy"' || true); \
	  starting=$$($(COMPOSE) $(COMPOSE_FILES) ps --format json 2>/dev/null | grep -c '"Health":"starting"' || true); \
	  rp_init=$$($(COMPOSE) $(COMPOSE_FILES) ps redpanda-init --format json 2>/dev/null | grep -c '"State":"exited"' || true); \
	  mn_init=$$($(COMPOSE) $(COMPOSE_FILES) ps minio-init --format json 2>/dev/null | grep -c '"State":"exited"' || true); \
	  if [ "$$unhealthy" = "0" ] && [ "$$starting" = "0" ] && [ "$$rp_init" != "0" ] && [ "$$mn_init" != "0" ]; then \
	    echo "All core services healthy; init jobs finished."; \
	    exit 0; \
	  fi; \
	  sleep 2; \
	  i=$$((i+1)); \
	done; \
	echo "WARNING: timed out waiting for full health. Current status:"; \
	$(COMPOSE) $(COMPOSE_FILES) ps; \
	exit 1

migrate: ## Database migrations
	@echo "ERROR: migrate not implemented yet (Phase 5 — Alembic)."
	@exit 1

seed: ## Seed demo data
	@echo "ERROR: seed not implemented yet (Phase 5)."
	@exit 1

test: ## Run Python unit tests
	@command -v uv >/dev/null 2>&1 || { echo "ERROR: uv is not installed."; exit 1; }
	uv run pytest tests/unit -m unit
	@if [ -d apps/web/node_modules ]; then \
	  cd apps/web && npm test; \
	else \
	  echo "SKIP: apps/web/node_modules missing — run make sync-web"; \
	fi

lint: ## Lint Python and TypeScript
	@command -v uv >/dev/null 2>&1 || { echo "ERROR: uv is not installed."; exit 1; }
	uv run ruff check apps services packages tests scripts ml || true
	@if [ -d apps/web/node_modules ]; then \
	  cd apps/web && npm run lint; \
	else \
	  echo "SKIP: frontend lint — run make sync-web"; \
	fi

format: ## Format code
	@command -v uv >/dev/null 2>&1 || { echo "ERROR: uv is not installed."; exit 1; }
	uv run ruff format apps services packages tests scripts ml || true
	@if [ -d apps/web/node_modules ]; then \
	  cd apps/web && npm run format; \
	fi

typecheck: ## Typecheck Python and TypeScript
	@command -v uv >/dev/null 2>&1 || { echo "ERROR: uv is not installed."; exit 1; }
	uv run mypy packages apps/api services || true
	@if [ -d apps/web/node_modules ]; then \
	  cd apps/web && npm run typecheck; \
	fi

demo: ## Run primary cooling demo
	@echo "ERROR: demo script not implemented yet (Phase 17)."
	@echo "Planned: scripts/demo/run_cooling_failure_demo.py"
	@exit 1

reset: ## Reset simulation / local volatile state
	@echo "ERROR: reset not implemented yet (Phase 3+)."
	@exit 1

train-models: ## Train ML models
	@echo "ERROR: train-models not implemented yet (Phase 8)."
	@exit 1

compose-validate: ## Validate compose file
	$(COMPOSE) $(COMPOSE_FILES) config >/dev/null && echo "docker compose config OK"
