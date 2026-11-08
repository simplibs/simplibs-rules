# HANDOFF — simplibs-rules: chybová hláška u slovníků ukazuje pořadí místo klíče

Handout pro samostatné vlákno v knihovně `simplibs-rules`. Vzniklo při práci na
`validate_call` (`**kwargs: X`), ale týká se **každé** validace slovníku.
Postup podle zvyku: nejdřív kód s design notes, pak testy, pak dokumentace.

---

## 1. Co je dnes špatně

Pravidlo pro `dict[K, V]` / `Mapping[K, V]` (a `MutableMapping`, `typing.Dict`, …) hlásí
selhání s popiskem (labelem) podle **pořadí** položky, ne podle klíče.

Ověřeno na aktuálním kódu (`build_typing_rule(dict[str, int])`, `value_name="opts"`):

| Vstup                    | Co selhalo        | Dnešní label | Čekaný label       |
| :----------------------- | :---------------- | :----------- | :----------------- |
| `{"a": 1, "b": "x"}`     | hodnota `"x"`     | `opts[1]`    | `opts['b']`        |
| `{1: 1}`                 | klíč `1`          | `opts[0]`    | (označení klíče)   |
| `{"a": 1, "zz": "x"}`    | hodnota `"x"`     | `opts[1]`    | `opts['zz']`       |

Dva problémy najednou:

1. **Index místo klíče.** U `**kwargs` uživatel hledá parametr podle jména, ne podle pořadí.
2. **Klíč a hodnota jsou nerozlišitelné.** `opts[0]` může být špatný klíč i špatná hodnota
   první položky; z labelu to poznat nejde (jen z textu zprávy).

`describe()` problém nemá (vrací `dict[str, int]`), mění se jen label chybové hlášky.

## 2. Proč to tak je

`build_key_value_rule` skládá slovník takto:

```python
parts.append(Compose(lambda mapping: mapping.keys(),   ForEach(key_rule)))
parts.append(Compose(lambda mapping: mapping.values(), ForEach(value_rule)))
```

`Compose` předá do `ForEach` jen pohled `.keys()` / `.values()`, takže klíč u hodnoty
zmizí. `ForEach.build_exception` pak zná jen `enumerate` index (`f"{value_name}[{index}]"`).
Chyba tedy není v `ForEach` ani v `Compose` samotných, ale v tom, že informace o klíči se
zahodí dřív, než se hláška staví.

## 3. Co se týká a co ne

* Týká se: každé validace `dict[K, V]`, `Mapping[K, V]`, `MutableMapping[K, V]`,
  `typing.Dict` apod. přes `build_typing_rule` (tedy i `IsTyping`, `validate_call`,
  `validate_dataclass`). U `validate_call` se nejvíc projeví u `**kwargs: X`.
* Netýká se: `list`, `set`, `tuple`, `Iterable` (tam je index správný popisek), ani
  `describe()`.
* `simplibs-validate` žádnou změnu **nepotřebuje** — hlášky se zlepší samy po nainstalování
  nové verze rules. Moje testy ve validate o labelech nic netvrdí.

## 4. Navržené řešení

Dvě nové malé kontejnerové pravidla vedle `ForEach`, která dostanou **přímo slovník**
(žádný `Compose`, takže klíč zůstane k dispozici):

* `ForEachValue(rule)` — každá hodnota slovníku musí splnit `rule`.
* `ForEachKey(rule)` — každý klíč slovníku musí splnit `rule`.

`build_key_value_rule` pak místo dvojice `Compose(...ForEach...)` použije
`ForEachKey(key_rule)` a `ForEachValue(value_rule)`.

Chování nových pravidel:

* `is_valid`: vstup musí být `Mapping`, jinak `False`; pak `all(...)` přes klíče / hodnoty.
* `describe`: `each key: <rule>` / `each value: <rule>` (obdoba `each <rule>` u `ForEach`),
  se stejným pravidlem o závorkách u složených pravidel (`AllOf`, `AnyOf`, `Compose`).
* `build_exception`: když vstup není mapování, delegovat na `IsInstance(Mapping)`;
  jinak najít první selhávající položku a zavolat `build_child_exception(...)` s labelem
  podle klíče. Fallback `..._UNREACHABLE_ERROR` podle vzoru `FOR_EACH_UNREACHABLE_ERROR`.
* Konstruktor: stejná kontrola „argument je volatelný“ jako u `ForEach`
  (`raise_rule_param_not_callable` — rozšířit seznam názvů a příklad o nová pravidla).

### Formát labelu (rozhodnutí, které je potřeba udělat)

* **Hodnota:** `opts['b']` — shodné se zápisem v Pythonu, klíč přes `repr`.
  Bez jména: `['b']`.
* **Klíč:** klíč nejde „indexovat“, tak potřebuje vlastní tvar. Doporučuji
  `opts (key 'zz')`; bez jména `(key 'zz')`. Alternativa: `key 'zz' of opts`.

Otevřené drobnosti: velmi dlouhý nebo složitý klíč (zkrátit `repr`?), a pořadí kontroly
(dnes AllOf: nejdřív klíče, pak hodnoty — ponechat).

## 5. Co jsem zvažoval a zavrhl

* **Změnit `ForEach`, aby u mapování procházel `.items()`.** Rozbilo by to stávající
  význam (`ForEach` nad slovníkem dnes prochází klíče) — nevratná změna chování.
* **Přidat do `ForEach` parametr pro pojmenování položek.** Nepomůže, protože `Compose`
  klíče zahazuje dřív; museli bychom měnit i `Compose`.
* **Nechat jak je.** Funguje to, hláška vždy říká hodnotu i typ; zisk je čistě v čitelnosti.
  Proto to není naléhavé a patří do vlákna rules, až tam budeš dělat jiné změny.

## 6. Soubory, kterých se změna dotkne (v rules)

Názvy odpovídají struktuře, kterou jsem viděl v zipu; cesty si před prací ověř.

1. `containers/ForEachKey.py` a `containers/ForEachValue.py` — nová pravidla (+ `_DESIGN_NOTES`).
2. `containers/__init__.py` — import a řádky v tabulce komponent.
3. `containers/_init_validators/raise_rule_param_not_callable.py` — rozšířit `Literal` názvů a
   slovník příkladů.
4. `predicates/typing/_builders/build_key_value_rule.py` — použít nová pravidla; upravit
   design notes (sekce 1 už mluví o `Compose` + `ForEach`).
5. Kořenový `__init__.py` knihovny — import, snake-case zkratky (`for_each_key`,
   `for_each_value`, podle vzoru `for_each = ForEach`), jmenný prostor `rule_class`,
   jmenný prostor `rules` a `__all__`.
6. README knihovny (tabulka pravidel: třída / zkratka / podpis) a `CHANGELOG.md`.

## 7. Testy (zrcadlí strukturu)

* Nová pravidla: `assert_rule_contract` (is_valid, `validate` režimy, `build_exception`) +
  vlastní testy labelů: hodnota podle klíče, klíč podle označení, bez `value_name`,
  nemapování na vstupu, prázdný slovník (projde), první selhávající položka, složený
  vnitřní rule (`AnyOf`) v `describe`.
* `build_key_value_rule`: nové očekávané labely pro `dict[str, int]` (tabulka v bodu 1).
* **Pozor na stávající testy:** zkontrolovat, jestli některý test u slovníkových
  anotací netvrdí starý label (`...[0]`, `...[1]`). Já testy rules neviděl.

## 8. Verze a dopad na ostatní

* Nová veřejná pravidla + změna textu labelu → další **minor** verze `simplibs-rules`.
  V changelogu do „Added“ nová pravidla, do „Changed“ nový tvar labelu u slovníků
  (kdo by label parsoval, bude potřebovat úpravu — nepravděpodobné).
* `simplibs-validate` má závislost `simplibs-rules>=0.4.0`. Zvyšovat ji je potřeba jen tehdy,
  pokud chceš ve validate dokumentaci slibovat názvy klíčů v hláškách.

## 9. Shrnutí rozhodnutí pro začátek vlákna

1. Souhlasíš s dvojicí `ForEachKey` / `ForEachValue` místo `Compose` + `ForEach`?
2. Tvar labelu: hodnota `opts['b']`; klíč `opts (key 'zz')` nebo `key 'zz' of opts`?
3. Zkracovat dlouhé klíče v labelu?
