from .build_annotated_rule import build_annotated_rule
from .build_any_of_rule import build_any_of_rule
from .build_callable_rule import build_callable_rule
from .build_elements_rule import build_elements_rule
from .build_key_value_rule import build_key_value_rule
from .build_literal_rule import build_literal_rule
from .build_tuple_rule import build_tuple_rule
from .build_type_rule import build_type_rule
from .ORIGIN_TABLE import ORIGIN_TABLE


_DESIGN_NOTES = """
# Typing Builders Sub-Package

## Purpose
Specialized builder functions that decompose Python `typing` annotations into
composed `simplibs-validate` rules. Each builder handles a distinct structural
shape (e.g. elements, key-value mappings, unions, tuples, literals) and
translates typing constructs into runtime executable Rule trees.

## Internal Components Registry

| Component               | Type     | Description                                                                        |
| :---------------------- | :------- | :--------------------------------------------------------------------------------- |
| `build_annotated_rule`  | Function | Processes `Annotated[T, ...]` unwrapping metadata and folding Rule predicates.     |
| `build_any_of_rule`     | Function | Processes `Union[A, B]` / `A | B` into an `AnyOf` composed rule.                   |
| `build_callable_rule`   | Function | Processes `Callable[...]` into an `IsCallable` check.                              |
| `build_elements_rule`   | Function | Processes container generics (`list[T]`, `set[T]`, etc.) into `ForEach` rules.     |
| `build_key_value_rule`  | Function | Processes mapping generics (`dict[K, V]`) into key and value checks via Compose.   |
| `build_literal_rule`    | Function | Processes `Literal[...]` into an `IsIn` rule over exact allowed values.            |
| `build_tuple_rule`      | Function | Routes tuple annotations to positional or elements builders based on shape.        |
| `build_type_rule`       | Function | Processes `Type[T]` / `type[T]` into `IsType` and `IsSubclass` checks.             |
| `ORIGIN_TABLE`          | Dict     | Registry mapping standard `get_origin` constructs to specialized builder handlers. |

"""