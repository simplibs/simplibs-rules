from .Regex import Regex
from .Contains import Contains
from .StartsWith import StartsWith
from .EndsWith import EndsWith
from .IsBlank import IsBlank
from .NotBlank import NotBlank
from .IsString import IsString
from .IsSubstringOf import IsSubstringOf
from .IsAlpha import IsAlpha
from .IsAlnum import IsAlnum
from .IsDigitString import IsDigitString
from .IsAscii import IsAscii
from .IsLowercase import IsLowercase
from .IsUppercase import IsUppercase
from .IsTitlecase import IsTitlecase


_DESIGN_NOTES = """
# String Predicate Rules Sub-Package

## Purpose
Predicate rules operating on `str` values — pattern matching, substring
and affix checks, and blank/non-blank content checks.

## Internal Components Registry

| Component      | Type  | Description                                                              |
| :------------- | :---- | :----------------------------------------------------------------------- |
| `Regex`        | Class | String must match a given regular expression pattern.                    |
| `Contains`     | Class | String must contain a given substring.                                   |
| `StartsWith`   | Class | String must start with a given prefix.                                   |
| `EndsWith`     | Class | String must end with a given suffix.                                     |
| `IsBlank`      | Class | String must be empty or whitespace-only.                                 |
| `NotBlank`     | Class | String must contain at least one non-whitespace character.               |
| `IsString`     | Class | Value must be strictly a `str`.                                          |
| `IsSubstringOf` | Class | String value must be a substring of a target string.                     |
| `IsAlpha`      | Class | String must consist entirely of alphabetic characters (non-empty).       |
| `IsAlnum`      | Class | String must consist entirely of alphanumeric characters (non-empty).     |
| `IsDigitString`| Class | String must consist entirely of digit characters (non-empty).            |
| `IsAscii`      | Class | String must contain only ASCII characters.                               |
| `IsLowercase`  | Class | String must be entirely lowercase (with at least one cased character).   |
| `IsUppercase`  | Class | String must be entirely uppercase (with at least one cased character).   |
| `IsTitlecase`  | Class | String must be title-cased.                                              |
"""