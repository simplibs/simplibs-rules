# 📦 `rules/predicates/strings` — String Content Rules

The `strings` package holds every rule that checks the *content* of a string —
substring/prefix/suffix membership, blankness, regex matching, and the reverse
"substring of" relationship — layered on top of a base `isinstance(value, str)` check
every rule in this package performs itself.

```python
from ..base_class import Rule

class Regex(Rule):
    ...
```

## A note on the shared `isinstance(value, str)` guard

Every rule in this package checks `isinstance(value, str)` as the first half of its
`is_valid` condition, using Python's short-circuit `and` so the string-specific method
(`.endswith()`, `.strip()`, `in`, ...) is never called on a non-string value. This
keeps each rule's `is_valid` a clean boolean expression rather than a `try/except
AttributeError` — a non-string input simply fails the first condition and never
reaches the second.

---

## 🧭 Table of Contents

* [`IsString`](#isstring)
* [`Contains`](#contains)
* [`IsSubstringOf`](#issubstringof)
* [`StartsWith`](#startswith)
* [`EndsWith`](#endswith)
* [`Regex`](#regex)
* [`IsBlank`](#isblank)
* [`NotBlank`](#notblank)
* [`IsAlnum`](#isalnum)
* [`IsAlpha`](#isalpha)
* [`IsAscii`](#isascii)
* [`IsDigitString`](#isdigitstring)
* [`IsLowercase`](#islowercase)
* [`IsTitlecase`](#istitlecase)
* [`IsUppercase`](#isuppercase)
* [`IsIdentifier`](#isidentifier)
* [`IsPrintable`](#isprintable)
* [`IsWhitespace`](#iswhitespace)

[⬅️ Back to main README](../../README.md#predicatesstrings--string-content)

---

### `IsString`

Value must be a string.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsString())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return isinstance(value, str)
```

[▲ Back to top](#-table-of-contents)

---

### `Contains`

String value must contain a given substring anywhere within it.

**Parameters:**
* `substring` (*str*): The substring that must be present.

**Example usage:**
```python
validate(value, Contains("@"))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and self.substring in value
    )
```

[▲ Back to top](#-table-of-contents)

---

### `IsSubstringOf`

The **inverse** relationship of `Contains`: the value itself must appear *within* a
given target string, rather than containing something.

**Parameters:**
* `target_string` (*str*): The string the value must be found inside of.

**Example usage:**
```python
validate(value, IsSubstringOf("ADMIN_ROLE_FULL_ACCESS"))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value in self.target_string
    )
```

[▲ Back to top](#-table-of-contents)

---

### `StartsWith`

String value must start with a given prefix.

**Parameters:**
* `prefix` (*str*): The required prefix.

**Example usage:**
```python
validate(value, StartsWith("https://"))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.startswith(self.prefix)
    )
```

[▲ Back to top](#-table-of-contents)

---

### `EndsWith`

String value must end with a given suffix.

**Parameters:**
* `suffix` (*str*): The required suffix.

**Example usage:**
```python
validate(value, EndsWith(".py"))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.endswith(self.suffix)
    )
```

[▲ Back to top](#-table-of-contents)

---

### `Regex`

String value must match a given regular expression pattern — searched anywhere in the
string (via `re.search`), not required to match from the start or the whole string.
The pattern is compiled once at construction, not on every validation, and an invalid
pattern is rejected immediately rather than failing on first use.

**Parameters:**
* `pattern` (*str*): The regular expression pattern to search for.

**Example usage:**
```python
validate(value, Regex(r"^[a-z]+$"))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and self.compiled.search(value) is not None
    )
```

[▲ Back to top](#-table-of-contents)

---

### `IsBlank`

String value must be empty or contain only whitespace.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsBlank())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.strip() == ""
    )
```

[▲ Back to top](#-table-of-contents)

---

### `NotBlank`

String value must contain at least one non-whitespace character — the direct inverse
of `IsBlank`, implemented independently for a more specific diagnostic message.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, NotBlank())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.strip() != ""
    )
```

[▲ Back to top](#-table-of-contents)

---

### `IsAlnum`

String value must be non-empty and consist solely of alphanumeric characters (letters and digits).

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsAlnum())
```

**Under the hood** *(`is_valid`)*:

```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.isalnum()
    )
```

On failure, the diagnostic distinguishes non-string types from empty or non-alphanumeric strings.

[▲ Back to top](#-table-of-contents)

---

### `IsAlpha`

String value must be non-empty and consist solely of alphabetic characters (letters).

**Parameters:**

* *(none — takes only `self`)*

**Example usage:**

```python
validate(value, IsAlpha())
```

**Under the hood** *(`is_valid`)*:

```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.isalpha()
    )
```

On failure, the diagnostic distinguishes non-string types from empty or non-alphabetic strings.

[▲ Back to top](#-table-of-contents)

---

### `IsAscii`

String value must consist entirely of ASCII characters (U+0000 to U+007F). Accepts empty strings.

**Parameters:**

* *(none — takes only `self`)*

**Example usage:**

```python
validate(value, IsAscii())
```

**Under the hood** *(`is_valid`)*:

```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.isascii()
    )
```

On failure, the diagnostic distinguishes non-string types from strings containing non-ASCII characters.

[▲ Back to top](#-table-of-contents)

---

### `IsDigitString`

String value must be non-empty and consist solely of numeric digit characters (`0`-`9`).

**Parameters:**

* *(none — takes only `self`)*

**Example usage:**

```python
validate(value, IsDigitString())
```

**Under the hood** *(`is_valid`)*:

```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.isdigit()
    )
```

On failure, the diagnostic distinguishes non-string types from empty or non-digit strings.

[▲ Back to top](#-table-of-contents)

---

### `IsLowercase`

String value must be entirely lowercase (must contain at least one cased character and no uppercase characters).

**Parameters:**

* *(none — takes only `self`)*

**Example usage:**

```python
validate(value, IsLowercase())
```

**Under the hood** *(`is_valid`)*:

```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.islower()
    )
```

On failure, the diagnostic distinguishes non-string types from strings containing uppercase characters or lacking cased characters.

[▲ Back to top](#-table-of-contents)

---

### `IsTitlecase`

String value must be title-cased (uppercase characters may only follow uncased characters and lowercase characters only follow cased ones).

**Parameters:**

* *(none — takes only `self`)*

**Example usage:**

```python
validate(value, IsTitlecase())
```

**Under the hood** *(`is_valid`)*:

```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.istitle()
    )
```

On failure, the diagnostic distinguishes non-string types from non-title-cased strings.

[▲ Back to top](#-table-of-contents)

---

### `IsUppercase`

String value must be entirely uppercase (must contain at least one cased character and no lowercase characters).

**Parameters:**

* *(none — takes only `self`)*

**Example usage:**

```python
validate(value, IsUppercase())
```

**Under the hood** *(`is_valid`)*:

```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.isupper()
    )
```

On failure, the diagnostic distinguishes non-string types from strings containing lowercase characters or lacking cased characters.

[▲ Back to top](#-table-of-contents)

---

### `IsIdentifier`

String value must be a valid Python identifier (letters, digits, underscores, not starting with a digit).

**Parameters:**

* *(none — takes only `self`)*

**Example usage:**

```python
validate(value, IsIdentifier())

```

**Under the hood** *(`is_valid`)*:

```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.isidentifier()
    )

```

On failure, the diagnostic distinguishes non-string types from invalid Python identifier strings.

[▲ Back to top](#-table-of-contents)

---

### `IsPrintable`

String value must consist entirely of printable characters or be empty.

**Parameters:**

* *(none — takes only `self`)*

**Example usage:**

```python
validate(value, IsPrintable())

```

**Under the hood** *(`is_valid`)*:

```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.isprintable()
    )

```

On failure, the diagnostic distinguishes non-string types from strings containing unprintable/control characters.

[▲ Back to top](#-table-of-contents)

---

### `IsWhitespace`

String value must be non-empty and consist solely of whitespace characters.

**Parameters:**

* *(none — takes only `self`)*

**Example usage:**

```python
validate(value, IsWhitespace())

```

**Under the hood** *(`is_valid`)*:

```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.isspace()
    )

```

On failure, the diagnostic distinguishes non-string types from empty or non-whitespace strings.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#predicatesstrings--string-content)