# CHIMERA AUTARCH — AI and Copilot Policy

This policy governs the expected use of AI coding assistants (including GitHub Copilot, ZenCoder, and other generative assistants) for code generation or suggestion in this repository. It is aligned to our `.github/copilot-instructions.md` and the project's architecture patterns.

## Goals

- Ensure AI-generated code is consistent with existing architectural and styling patterns.
- Maintain secure, testable, and maintainable code.
- Avoid introducing unsupported language or library features.

## Rules (must-follow)

1. Respect Version Constraints
   - Only use language features and libraries compatible with versions defined in `requirements*.txt`, `pyvenv.cfg`, and `Dockerfile`.
   - For Python code, target Python 3.12.

2. Match Project Patterns
   - Follow the _event-driven_ architecture: `HeartNode`, `ToolRegistry`, `MetacognitiveEngine`, and `PersistenceLayer`.
   - Use `dataclass` for configuration DTOs.
   - Use `async def` for I/O and network code, `ThreadPoolExecutor` for blocking operations.

3. Tests Required
   - Any non-trivial addition or change must include unit tests matching existing test patterns (see `tests/` and `tests/test_core.py`).
   - If the change touches multiple components, include integration tests and instructions to reproduce the behavior.

4. Security & Secrets
   - Never hardcode secrets or tokens in code. Use environment variables or the configuration system.
   - Use existing cryptographic patterns (e.g., `QuantumEntropy.sign_message`) for message signing.

5. Documentation & Docstrings
   - Maintain docstrings consistent with existing style: short module-level docstrings and brief per-function/class docstrings.
   - Document configuration options in `config.example.yaml` and add to `README.md` where appropriate.

6. Code Formatting & Linting
   - Follow PEP8 where appropriate; prefer `black` and `ruff` if present in CI.
   - Keep lines short and functions minimal.

7. Avoid Architecture Changes Without PR
   - Do not alter the global architecture (HeartNode / ToolRegistry / Metacog / Persistence) without a PR that includes design rationale, tests, and migration notes.

## AI-Assisted PR Best Practices

- Before opening a PR, review and run the test suite: `.\run_tests.ps1`.
- Validate that generated code follows the `copilot-instructions.md` and doesn't enable unsupported versions.
- Review logging and error handling in generated code for consistency.

## Enforcement

- Changes introduced by Copilot or other assistants must be accompanied by a human reviewer in the PR.
- The PR checklist (see `.github/pull_request_template.md`) includes items that require enforcement by CI and reviewers.

---

If you have questions about this policy or believe a change requires broader architectural adjustments, open an issue with the design rationale and tag the repo maintainers.
