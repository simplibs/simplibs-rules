from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_invalid_predicate(rule: Any) -> NoReturn:
    """Vyvolá ParamError, pokud objekt není typu Rule ani Callable."""

    raise ParamError(
        error_name="INVALID_PREDICATE_TARGET",
        label="pravidlo / predikát",
        value=type(rule).__name__,
        problem=(
            f"Očekávána instance Rule nebo Callable, získáno: '{type(rule).__name__}'.",
            "Předaný objekt nelze vyhodnotit jako pravidlo validace.",
        ),
        expected="Instance třídy Rule nebo funkce vracející bool.",
        how_to_fix=(
            "Předejte jako pravidlo instanci odvozenou od třídy Rule nebo obyčejnou funkci / lambdu.",
            "Příklad: IsGreaterThan(0) nebo lambda x: x > 0",
        ),
        exception=TypeError,
    )