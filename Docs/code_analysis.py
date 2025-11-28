"""
Static code analysis helpers for AST-based function metrics and suggestions.

Fix: Implemented FunctionVisitor used by analyze_and_suggest_patch, which was
previously referenced but undefined. The visitor gathers function-level metrics
to produce optimization suggestions.
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass
from typing import Dict, List, Set, Optional

logger = logging.getLogger("chimera")

# Heuristic list for IO and common I/O call names
_IO_CALL_NAMES = {
    "print",
    "open",
    "input",
    "read",
    "write",
    "recv",
    "send",
    "sendall",
    "requests.get",
    "requests.post",
    "requests.put",
    "requests.delete",
}


@dataclass
class FunctionInfo:
    name: str
    lineno: int
    end_lineno: int
    loops: int = 0
    io_calls: int = 0
    calls: Set[str] = None
    recursion: bool = False
    branches: int = 0

    def __post_init__(self):
        if self.calls is None:
            self.calls = set()


class FunctionVisitor(ast.NodeVisitor):
    """
    AST visitor that gathers function-level metrics:
      - number of loops
      - number of "IO" calls
      - calls to other functions (set)
      - recursion detection
      - number of branches (If, BoolOp)
    """

    def __init__(self) -> None:
        super().__init__()
        self.functions: Dict[str, FunctionInfo] = {}
        self._current: Optional[str] = None
        self._stack: List[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # pragma: no cover - trivial
        name = node.name
        self._stack.append(name)
        self._current = name
        info = FunctionInfo(
            name=name,
            lineno=node.lineno,
            end_lineno=getattr(node, "end_lineno", node.lineno),
        )
        self.functions[name] = info

        # Visit body to collect metrics
        for child in node.body:
            self.visit(child)

        # Restore
        self._stack.pop()
        self._current = self._stack[-1] if self._stack else None

    # Loops
    def visit_For(self, node: ast.For) -> None:
        self._incr_metric("loops")
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._incr_metric("loops")
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self._incr_metric("loops")
        self.generic_visit(node)

    # Branches: ifs, boolean operations
    def visit_If(self, node: ast.If) -> None:
        self._incr_metric("branches")
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self._incr_metric("branches")
        self.generic_visit(node)

    # Calls
    def visit_Call(self, node: ast.Call) -> None:
        call_name = self._get_call_name(node)
        if call_name:
            self._record_call(call_name)
            # IO detection (simple heuristic)
            if any(call_name == io_name or call_name.endswith("." + io_name.split(".")[-1])
                   for io_name in _IO_CALL_NAMES):
                self._incr_metric("io_calls")
            if self._current and call_name == self._current:
                # recursion detected
                self._set_recursion(True)
        self.generic_visit(node)

    # Helper for expressions that may contain branches
    def visit_Compare(self, node: ast.Compare) -> None:
        # comparisons generally add to complexity/branches
        self._incr_metric("branches")
        self.generic_visit(node)

    # Utility helpers
    def _incr_metric(self, metric: str, amount: int = 1) -> None:
        if not self._current:
            return
        info = self.functions.get(self._current)
        if not info:
            return
        if metric == "loops":
            info.loops += amount
        elif metric == "io_calls":
            info.io_calls += amount
        elif metric == "branches":
            info.branches += amount

    def _record_call(self, call_name: str) -> None:
        if not self._current:
            return
        info = self.functions.get(self._current)
        if info:
            info.calls.add(call_name)

    def _set_recursion(self, value: bool) -> None:
        if not self._current:
            return
        info = self.functions.get(self._current)
        if info:
            info.recursion = value

    @staticmethod
    def _get_call_name(node: ast.Call) -> Optional[str]:
        """
        Resolve a readable "dotted" call name for a Call node, e.g.:
          - Name(id='open') -> "open"
          - Attribute(value=Name(id='requests'), attr='get') -> "requests.get"
          - nested attributes are expanded: a.b.c -> "a.b.c"
        """
        func = node.func
        parts: List[str] = []
        while True:
            if isinstance(func, ast.Name):
                parts.append(func.id)
                break
            if isinstance(func, ast.Attribute):
                parts.append(func.attr)
                func = func.value
                continue
            # other types (e.g., Lambda) â€“ can't resolve
            return None
        # parts were built from leaf to root; reverse
        return ".".join(reversed(parts))


def analyze_and_suggest_patch(source: str) -> Dict[str, List[Dict[str, object]]]:
    """
    Analyze Python source, return function metrics and heuristic suggestions.

    Returns:
      {
        "functions": [
          {
            "name": str,
            "lineno": int,
            "end_lineno": int,
            "loops": int,
            "io_calls": int,
            "branches": int,
            "calls": [...],
            "recursion": bool,
            "suggestions": [...]
          },
          ...
        ]
      }
    """
    try:
        tree = ast.parse(source)
        visitor = FunctionVisitor()
        visitor.visit(tree)

        result = {"functions": []}
        for fn in visitor.functions.values():
            suggestions: List[str] = []
            # Heuristic rules
            if fn.loops > 0 and fn.io_calls > 0:
                suggestions.append(
                    "Detected I/O operations inside loops. Consider buffering or moving I/O "
                    "outside the loop to reduce latency and syscalls."
                )
            if fn.recursion:
                suggestions.append(
                    f"Function '{fn.name}' calls itself (recursion). Consider iterative approaches "
                    "or tail recursion optimization if applicable for performance and stack safety."
                )
            if fn.branches > 4:
                suggestions.append(
                    "High branching complexity detected. Consider simplifying conditionals or "
                    "extracting logic into helper functions."
                )
            if len(fn.calls) > 8:
                suggestions.append(
                    "Large number of distinct calls; consider refactoring to reduce coupling and improve testability."
                )
            # Provide a lightweight "complexity score"
            complexity_score = fn.loops + fn.branches + max(0, fn.io_calls // 1)
            if complexity_score >= 10:
                suggestions.append(
                    f"Complexity score {complexity_score} suggests this function may be doing too much. Try to break it up."
                )
            # Add results
            result["functions"].append({
                "name": fn.name,
                "lineno": fn.lineno,
                "end_lineno": fn.end_lineno,
                "loops": fn.loops,
                "io_calls": fn.io_calls,
                "branches": fn.branches,
                "calls": sorted(fn.calls),
                "recursion": fn.recursion,
                "suggestions": suggestions,
            })
        return result
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("analyze_and_suggest_patch failed: %s", exc)
        # Return a structured error-like result to calling code
        return {"error": str(exc), "functions": []}
