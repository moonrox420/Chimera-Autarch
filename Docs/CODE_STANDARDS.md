# CHIMERA AUTARCH — Code & Style Standards

This document consolidates style, naming, and architectural patterns derived from the existing project code (Python modules, PowerShell scripts, Dockerfile, tests and configuration files). The style guide is intentionally pragmatic: it documents what is already implemented so that contributors and AI copilots can remain consistent.

---

## Table of Contents

1. Python
2. PowerShell scripts
3. Docker / Deployment
4. Configuration
5. Testing
6. Logging & Error Handling
7. Security
8. Git & Pull Requests
9. Formatting & Linting
10. FAQs & Examples

---

## 1. Python (Primary language)

- Use `snake_case` for function and variable names, `CamelCase` for class names (existing code follows this (e.g., `QuantumEntropy`, `ToolRegistry`).
- Use `dataclasses` for configuration & simple data objects (examples: `ServerConfig`, `ChimeraConfig`).
- Prefer `type hints` for public signatures: `def f(x: str) -> int`.
- Use `async def` for I/O or network operations (websockets, aiosqlite). If a blocking call is required, run it with `ThreadPoolExecutor`.
- Use `Generic` and `TypeVar` for typed containers (e.g., `ToolResult[T]`).
- Document top-level modules with a short docstring. Each class and public function should have a brief docstring explaining intent and behavior.
- Use f-strings for string interpolation consistently.
- Keep SQL inline statements in persistence modules but simple. Use parameterized SQL where user data is involved.

### Error Handling

- Use explicit try/except blocks; log exceptions with `logger.error()` and include `traceback.format_exc()` if returning the error in a structured form.
- Avoid swallowing exceptions silently. If a function must return an error, return a typed error container (e.g., `ToolResult(False, error_str, metrics)`)

### Example: Registering a Tool

```py
from dataclasses import dataclass
from typing import Callable

async def example_tool(arg: str) -> str:
    return f"Hello {arg}"

tool = Tool(name="hello", func=example_tool, description="Says hello")
registry.register(tool)
```

## 2. PowerShell Scripts (Automation & Setup)

- Use `param()` block for script input and `[ValidateSet()]` for enumerated values.
- Set `$ErrorActionPreference = 'Stop'` or `Continue` depending on the script. Default the startup script to `Stop`.
- Use `Write-Host` with colors for user facing output. Implement `Write-Status` helper pattern for consistent status messages.
- Back up files before editing (e.g., `settings.json.bak.YYYYMMDD_HHMMSS`).
- Keep `Start-Process` calls for opening URLs or launching background processes.
- Validate CLI tooling availability (e.g., `code`, `docker`, `python`) early and provide remediations.

## 3. Docker / Deployment

- Use multi-stage Dockerfiles: `builder` stage with `pip install --user` then copying to final, ensuring `PATH` includes `/root/.local/bin`.
- Run as non-root user (UID 1000) for security.
- Expose necessary ports: `3001` (WebSocket), `3000` (Dashboard), `8080` (Federated Learning / Flower).
- Add a robust `HEALTHCHECK` to hit the `/metrics` endpoint.
- Use volumes for persistence and logs; consider explicit named volumes for production.

## 4. Configuration

- Use a `config.yaml` as the primary source and environment variables (all prefixed with `CHIMERA_`) to override settings.
- Provide `config.example.yaml` and sample `.env` file with key variables.
- Represent settings as typed dataclasses. Example usage: `config = load_config('config.yaml')`.
- Prefer dataclass fields to have default values where appropriate for safe fallback.

## 5. Testing

- Unit tests use `unittest` or `pytest` conventions (`tests/` contains test files). Use `asyncio.run()` for running async tests in `unittest`.
- Tests should be small and focused on single behavior; use `setUp()` and `tearDown()` for reusable fixtures.
- Testing runner: `run_tests.ps1` wraps `pytest` and optional coverage collection.

## 6. Logging & Error Handling

- Initialize logging once at start with `logging.basicConfig(...)`.
- Use a module-level `logger = logging.getLogger("chimera")` in main modules.
- Log at appropriate levels: `debug`, `info`, `warning`, `error`, `critical` and avoid noisy logs for normal operations.
- Prefer structured logging for key events where possible.

## 7. Security

- Use `QuantumEntropy` (secrets.token_urlsafe) or `os.urandom` for secure identifiers.
- Use `hashlib.sha3_256` for signing messages (HMAC-like approach) when verifying node messages.
- Keep sensitive files out of the repository and visible through `.gitignore` (e.g., `.env`, `chimera_memory.db` backups) and use secure storage for secrets.
- SSL: check `ssl/cert.pem` and `ssl/key.pem` in both `ssl/` subdirectory and root directory as automatic fallback.

## 8. Git & Pull Request Guidelines

- Use feature branches and descriptive commits.
- Include changelog updates in `RELEASE_NOTES_V2.2.md` and `PROJECT_STATUS.md` for major changes.
- Add tests for behavioral changes. Run `run_tests.ps1` before raising PR.

## 9. Formatting & Linting

- Enforce `pyproject` or `requirements` for tooling: `black` (code formatting) and `flake8` (linting) recommended.
- Set up a pre-commit or GitHub action if desired for CI.
- Python style: follow PEP8 where reasonable. Shorter lines, two blank lines between top-level functions, and single blank line between logical groups.

## 10. FAQs & Examples

- How to register a new `Tool`? Use the `Tool` and `ToolRegistry` pattern; add the `Tool` in `HeartNode._init_tools`.
- How to add a new config setting? Add a field in the appropriate dataclass, add to defaults in `config.save_default_config`, and document in `config.example.yaml`.
- How to add a new automated script? Put it in `scripts/` or `start.ps1`, use `param()` and consistent `Write-Status` pattern.

---

If you'd like, I can:
- Add this guide to `.github/CODE_STANDARDS.md` and link it from `README.md`.
- Create a `pyproject.toml` with `black`, `ruff`/`flake8`, and `isort` for automatic formatting.
- Add GitHub Actions skeleton for linting and unit tests.

What would you like me to do next? (Options: implement `pyproject.toml`, add the guide file to the repo, or generate CI configuration.)
