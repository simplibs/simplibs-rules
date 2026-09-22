from typing import Any, Container


def format_container(container: Container[Any]) -> str:
    """Format a container deterministically (sorting elements in sets/frozensets if possible)."""

    # 1. Handling for set-based collections (set, frozenset)
    if isinstance(container, (set, frozenset)):
        try:
            sorted_items = sorted(container)
        except TypeError:
            sorted_items = list(container)
        return "{" + ", ".join(repr(x) for x in sorted_items) + "}"

    # 2. Handling for all other container types (list, tuple, dict, etc.)
    return repr(container)


_DESIGN_NOTES = """
# format_container — Deterministic Container Formatter

## Purpose
Formats collections and containers into stable, deterministic string
representations suitable for exception messages, assertion output, and logging.

---

## 1. Execution Rationale & Performance

* **Deterministic Set Ordering:**
  Python's built-in `set` and `frozenset` types rely on hash randomization,
  causing `repr()` to output elements in non-deterministic order between runtime
  executions. `format_container` attempts to sort set elements (`sorted(container)`)
  before formatting.
* **Graceful Unsortable Fallback:**
  If a set contains unorderable mixed types (e.g., `{"a", 1}` throwing `TypeError`),
  it safely falls back to a deterministic list representation based on iteration.
* **Passthrough for Sequential Containers:**
  Types with guaranteed insertion or execution order (such as `list`, `tuple`,
  and `dict`) bypass the sorting step and rely directly on their native `repr()`.

---

## 2. Benefits for Exception Diagnostics

1. **Test Stability:** Prevents flaky unit tests when asserting exact `ValidationError`
   messages containing set parameters.
2. **Aggregated Logging:** Ensures error logs remain identical across worker
   processes and distributed instances, improving log grouping and trace analysis.
"""