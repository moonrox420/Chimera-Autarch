#!/usr/bin/env python3
"""Guard script to detect accidental non-Python content in Python source files.

This script searches all .py files in the workspace (excluding typical venv and build dirs)
and flags any lines that look like shell commands that were accidentally pasted into Python files,
such as PowerShell activate commands, direct `python -m pytest` or bare `./` usage at the start of a line.
"""
import re
from pathlib import Path
import sys

EXCLUDE_DIRS = {"droxai-env", "venv", "flwr-env", ".venv", "htmlcov", "release", ".git"}
SUSPECT_PATTERNS = [
    re.compile(r"(^|\s)(Activate\.ps1)(\s|$)"),
    re.compile(r"(^|\s)(python)\s+-m\s+pytest(\s|$)"),
    # Starting a line with ./ or .\
    re.compile(r"^(?:\./|\\\.\\)"),
]


def find_suspects(workspace: Path):
    suspects = []
    for path in workspace.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            # Skip lines that are Python comments or inside triple-quoted strings
            if stripped.startswith("#"):
                continue
            for pat in SUSPECT_PATTERNS:
                for m in pat.finditer(line):
                    start = m.start(0)
                    # Quick heuristic: ensure the match is not within quotes
                    # Count quotes before the match; if even, not inside a string
                    prefix = line[:start]
                    double_quotes = prefix.count('"')
                    single_quotes = prefix.count("'")
                    if (double_quotes % 2 == 0) and (single_quotes % 2 == 0):
                        suspects.append((path, i, line.strip()))
                        break
    return suspects


def main():
    base = Path(__file__).resolve().parents[1]
    suspects = find_suspects(base)
    if suspects:
        print("Suspect lines detected in Python files:")
        for p, ln, txt in suspects:
            print(f"{p}:{ln}: {txt}")
        print("Fix or comment out these lines before committing. Guard scripts can be disabled, but it's not recommended.")
        return 1
    print("No suspect lines found. All good.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

