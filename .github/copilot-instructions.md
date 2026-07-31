<!--
Auto-generated guidance for AI coding agents working in this workspace.
This file was created because the repository currently contains only a `venv/` folder
and no discoverable source files. The instructions below are intentionally concrete,
showing where to look and what to do next. Please update the placeholders once
the codebase is present so agents can operate without asking clarifying questions.
-->

# Copilot instructions for this repository

**Purpose**: help AI coding agents become productive quickly by documenting the
repository layout, common developer workflows, and project-specific patterns.

**Current repo state**: only `venv/` found at the repo root. No source files,
build config, or tests were discovered. Agents should ask the maintainer for the
project root if code lives outside the current workspace, or wait for the user
to add the source tree.

**Immediate checks (agent must run)**
- **Find agent docs**: look for `AGENT.md`, `AGENTS.md`, `.github/copilot-instructions.md` and `README.md`.
- **Locate source**: check for `pyproject.toml`, `requirements.txt`, `setup.py`, `package.json`, `src/`, or `app/`.
- **Environment**: note the existing `venv/` folder; do NOT modify it without user approval.

**Big-picture guidance (how to reason about this repo)**
- **If Python project:** expect an entrypoint in `src/`, `app/`, or top-level scripts. Look for `__main__.py`, `manage.py`, or `app.py`.
- **If multiple services:** expect folders like `services/`, `api/`, `worker/`. Treat each folder as a boundary and look for a local `requirements.txt` or `pyproject.toml` per service.
- **Config & secrets:** prefer `.env`, `config/*.yaml`, or `config/*.json`. Do not print secrets — redact any values you find and ask the user how to proceed.

**Dev workflows & commands (run only when corresponding files exist)**
- **Create / activate venv (Windows PowerShell):**
```
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```
- **Install deps (if `requirements.txt` exists):**
```
python -m pip install -r requirements.txt
```
- **Run tests (if tests discovered):**
```
python -m pytest -q
```
- **Run the app (common patterns):**
  - If `pyproject.toml`/`poetry.lock`: `poetry run python -m your_package`
  - If `app.py` or `main.py`: `python app.py` or `python main.py`

**Project-specific conventions to look for**
- **Import layout:** check whether package code imports from `src.` (PEP 420 style) or relative imports. Mirror the existing style.
- **Data models and serialization:** search for `schemas.py`, `models.py`, `pydantic` usage, or `dataclasses` and follow the chosen pattern.
- **Background jobs / queues:** search for `celery`, `rq`, `kombu`, or `kafka` references — treat those as integration points requiring env vars and broker URLs.

**Integration points & external dependencies**
- Look for `docker-compose.yml` or `Dockerfile` — these indicate containerized dev or service dependencies.
- Check for references to cloud SDKs (`boto3`, `google-cloud-*`, `azure-*`) — any credentials or project IDs must be redacted.
- If `openapi`, `swagger`, or `schemas/` exist, prefer generating / editing server/client code via those specs rather than hand-editing several endpoints.

**How to update this file (merge guidance for future agents)**
- If `.github/copilot-instructions.md` already exists, preserve any maintainer-written sections verbatim and append new discoveries under a new dated subsection like `## 2026-06-22: additions`.
- Avoid overwriting human-written rationale or architectural notes — instead add clarifying examples and concrete commands.

**Examples of actionable edits (templates for agents)**
- When adding a run instruction, include the exact file to run, e.g. `python -m src.server` or `python -m app`.
- When documenting a service boundary, cite the directory, e.g. "The `worker/` folder consumes messages from `redis://...` and writes to `data/processed/`."

**Questions for the maintainer (agent should ask these if missing)**
- Where is the application entrypoint (script/module)?
- Which Python version and packaging tool do you prefer (`pip`, `poetry`, `pipenv`)?
- Are there multiple services and where are their roots located?

---
If this file is helpful, I can: (1) refine it after you add the source tree, or (2) open a checklist PR that fills concrete commands once I can discover `requirements.txt`, `pyproject.toml`, or `Dockerfile`.
