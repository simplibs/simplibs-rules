_DESIGN_NOTES = """
# Predicates Sub-Package

## Purpose
Root registry and re-export point for all single-purpose atomic rules (predicates).
Predicates represent single, non-composite assertions evaluated directly against an
input value or its structural properties.

## Sub-Packages Registry

| Sub-Package        | Focus Area / Responsibility                                                         |
| :----------------- | :---------------------------------------------------------------------------------- |
| `arithmetic`       | Mathematical calculations and properties (tolerances, divisibility, remainders).    |
| `checkers`         | Parameterless boolean, identity, and emptiness state assertions.                    |
| `collections`      | Structure and contents of containers, sets, sequences, and mappings.                |
| `comparisons`      | Value-based relational operators (equality, inequality, order, numeric ranges).     |
| `introspection`    | Structural inspection of types, interfaces, attributes, callable states, and `len`. |
| `logic`            | Core identity (`is`) and collection membership (`in`) assertions with strict flags. |
| `numeric`          | Specific numeric domain type checks, non-finite values (`NaN`, `inf`), and `bool`.  |
| `strings`          | Textual contents, pattern matching, prefix/suffix checks, and whitespace states.    |
| `_helpers`         | Internal shared utilities for diagnostic rendering and predicate calculation logic. |
| `_init_validators` | Internal constructor assertion routines ensuring valid parameter boundaries.        |

## Exposed Components Registry

| Component                 | Category      | Description                                                                    |
| :------------------------ | :------------ | :----------------------------------------------------------------------------- |
| `AllOf`                   | Containers    | Logical AND composition (all child rules must pass).                          |
| `AnyOf`                   | Containers    | Logical OR composition (at least one child rule must pass).                   |
| `Compose`                 | Containers    | Sequential rule pipeline passing transformed data through steps.               |
| `ForEach`                 | Containers    | Applies an inner rule to every item in an iterable.                            |
| `NoneOf`                  | Containers    | Logical NOR composition (no child rule may pass).                              |
| `Not`                     | Containers    | Inverts the result of a single child rule.                                     |
| `CloseTo`                 | Arithmetic    | Verifies numeric proximity within a tolerance window.                          |
| `DivisibleBy`             | Arithmetic    | Verifies exact integer/numeric divisibility without remainder.                 |
| `HasRemainder`            | Arithmetic    | Verifies that division yields a non-zero remainder.                            |
| `IsEmpty`                 | Checkers      | Evaluates whether a container or string is empty.                              |
| `IsFalse`                 | Checkers      | Checks for boolean `False`.                                                    |
| `IsNone`                  | Checkers      | Checks for `None` identity.                                                    |
| `IsTrue`                  | Checkers      | Checks for boolean `True`.                                                     |
| `NotEmpty`                | Checkers      | Evaluates whether a container or string is non-empty.                          |
| `AllUnique`               | Collections   | Ensures all items in an iterable are distinct.                                 |
| `HasItem`                 | Collections   | Checks for presence of a specific value in a collection.                       |
| `HasKey`                  | Collections   | Checks for presence of a key in a mapping.                                     |
| `HasKeys`                 | Collections   | Checks for presence of multiple required keys in a mapping.                    |
| `IsContainer`             | Collections   | Asserts input implements container semantics.                                  |
| `IsSubsetOf`              | Collections   | Asserts input set/collection is a subset of an expected target.                |
| `IsSupersetOf`            | Collections   | Asserts input set/collection is a superset of an expected target.              |
| `Equals`                  | Comparisons   | Checks value equality (`==`).                                                  |
| `GreaterOrEqual`          | Comparisons   | Greater than or equal to (`>=`).                                               |
| `GreaterThan`             | Comparisons   | Strictly greater than (`>`).                                                   |
| `InRange`                 | Comparisons   | Validates value lies strictly within a lower and upper bound.                  |
| `LessOrEqual`             | Comparisons   | Less than or equal to (`<=`).                                                  |
| `LessThan`                | Comparisons   | Strictly less than (`<`).                                                      |
| `NotEquals`               | Comparisons   | Checks value inequality (`!=`).                                                |
| `HasAttribute`            | Introspection | Checks if an object possesses a specific named attribute.                      |
| `HasLength`               | Introspection | Validates object `len()` against exact or range constraints.                   |
| `IsCallable`              | Introspection | Asserts value is callable (functions, methods, classes with `__call__`).       |
| `IsDataclass`             | Introspection | Checks whether input is a dataclass instance or type.                          |
| `IsHashable`              | Introspection | Checks if an object implements hashability (`__hash__`).                       |
| `IsInstance`              | Introspection | Validates runtime type instance using `isinstance()`.                          |
| `IsIterable`              | Introspection | Checks if an object can be iterated over.                                      |
| `IsSubclass`              | Introspection | Validates class inheritance using `issubclass()`.                              |
| `IsType`                  | Introspection | Asserts input is a Python `type` object.                                       |
| `Is`                      | Logic         | Checks identity equality (`is`).                                               |
| `IsIn`                    | Logic         | Asserts value is contained in options (`in`), with optional `strict` typing.   |
| `IsNot`                   | Logic         | Checks identity inequality (`is not`).                                         |
| `NotIn`                   | Logic         | Asserts value is absent from options (`not in`), with optional `strict` typing.|
| `IsBool`                  | Numeric       | Checks strictly for boolean type (`bool`).                                     |
| `IsDecimal`               | Numeric       | Checks for `decimal.Decimal` instances.                                        |
| `IsEven`                  | Numeric       | Verifies numeric value is an even integer (excluding booleans).                |
| `IsFinite`                | Numeric       | Verifies value is a finite primitive number (excludes NaN and infinities).     |
| `IsFloat`                 | Numeric       | Checks for floating-point values.                                              |
| `IsInfinity`              | Numeric       | Verifies numeric value represents mathematical infinity (`inf`).               |
| `IsInteger`               | Numeric       | Checks for integer values (excluding booleans).                                |
| `IsNan`                   | Numeric       | Verifies numeric value is NaN (Not a Number).                                  |
| `IsNumber`                | Numeric       | Validates real numbers (int, float, Decimal).                                  |
| `IsOdd`                   | Numeric       | Verifies numeric value is an odd integer (excluding booleans).                 |
| `IsPi`                    | Numeric       | Checks if numeric value matches Archimedes' constant $\pi$.                    |
| `IsPrimitiveNumber`       | Numeric       | Asserts native primitive number types (`int`, `float`).                        |
| `IsZero`                  | Numeric       | Validates exact zero value across numeric types.                               |
| `Contains`                | Strings       | Checks substring presence within a target string.                              |
| `EndsWith`                | Strings       | Asserts string ends with given suffix.                                         |
| `IsAlnum`                 | Strings       | Verifies string is non-empty and consists solely of alphanumeric characters.   |
| `IsAlpha`                 | Strings       | Verifies string is non-empty and consists solely of alphabetic characters.     |
| `IsAscii`                 | Strings       | Asserts string consists entirely of ASCII characters.                          |
| `IsBlank`                 | Strings       | Verifies string consists solely of whitespace or is empty.                     |
| `IsDigitString`           | Strings       | Verifies string is non-empty and consists solely of numeric digits (`0`-`9`).  |
| `IsLowercase`             | Strings       | Verifies string contains only lowercase characters (and at least one cased).   |
| `IsString`                | Strings       | Asserts value is an instance of `str`.                                         |
| `IsSubstringOf`           | Strings       | Asserts value is a substring contained within a master string.                 |
| `IsTitlecase`             | Strings       | Verifies string is title-cased.                                                |
| `IsUppercase`             | Strings       | Verifies string contains only uppercase characters (and at least one cased).   |
| `NotBlank`                | Strings       | Verifies string contains non-whitespace characters.                            |
| `Regex`                   | Strings       | Matches string against a regular expression pattern.                           |
| `StartsWith`              | Strings       | Asserts string starts with given prefix.                                       |
| `IsAny`                   | Typing        | Structural counterpart to `typing.Any` that accepts any value.                 |
| `IsTyping`                | Typing        | Main rule for validating values against arbitrary supported type annotations.  |
| `build_typing_rule`       | Function      | Core entrypoint builder that translates type annotations into Rule instances.  |
| `get_supported_origins`   | Function      | Utility returning set of supported origins handled by the builder registry.    |
| `is_supported_annotation` | Function      | Utility checking whether a type annotation can be processed by `IsTyping`.     |

"""