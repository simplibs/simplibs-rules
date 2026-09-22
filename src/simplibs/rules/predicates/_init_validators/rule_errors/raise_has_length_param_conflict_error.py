from simplibs.exception import ParamError


def raise_has_length_param_conflict_error(
    length: int | None,
    min_length: int | None,
    max_length: int | None,
) -> None:
    """Raise a ParamError tailored to a parameter conflict in the HasLength rule."""

    # 1. Prepare data (identify the exact names of the conflicting parameters)
    conflicting = []
    if min_length is not None:
        conflicting.append("'min_length'")
    if max_length is not None:
        conflicting.append("'max_length'")

    range_str = " and ".join(conflicting)

    # 2. Build and raise the exception
    raise ParamError(
        error_name="PARAM_CONFLICT_ERROR",
        label="HasLength.length",
        expected="either 'length' or 'min_length'/'max_length', not both",
        value={"length": length, "min_length": min_length, "max_length": max_length},
        problem=f"Parameter 'length' ({length}) cannot be combined with {range_str}.",
        how_to_fix=(
            "Specify either 'length' for exact match OR 'min_length'/'max_length' for a range, do not mix them.",
            "Example: HasLength(length=5) OR HasLength(min_length=1, max_length=10)",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_has_length_param_conflict_error — Parameter Mutual Exclusivity Guard

## Purpose
Raises a tailored `ParamError` when mutually exclusive length parameters
(`length` vs `min_length`/`max_length`) are mixed during `HasLength`
instantiation.

---

## 1. Execution Rationale

* **Fail-Fast Conflict Prevention:**
  Prevents ambiguous length validation logic by ensuring exact length
  matching and range boundaries are never defined simultaneously.
* **Dynamic Conflict Formatting:**
  Inspects `min_length` and `max_length` dynamically to construct precise
  error messages identifying exact conflicting parameters.
"""
