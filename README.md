<div align="center">

# Python Topics — 16 Runnable Examples

Sixteen numbered, self-contained files: one core Python topic each, every file runnable on its own.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Examples](https://img.shields.io/badge/examples-16%2F16%20runnable-brightgreen.svg)](#file-index)
[![Tests](https://img.shields.io/badge/tests-passing-success.svg)](#verification)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)

**English** | [简体中文](README.zh-CN.md)

</div>

> The badges are static [shields.io](https://shields.io/) labels describing the intended state of this repository. There is no CI workflow here, so nothing is claimed to pass automatically — the [Verification](#verification) section records the exact commands and the result of the last run.

## Why this repo

Most Python material shows snippets. Snippets hide the parts that actually cause bugs: the import, the encoding, the mutable default, the `__main__` guard.

This repository is the opposite: **16 numbered scripts, each about one topic, each of which you can run immediately** with nothing but the standard library.

- **Runnable, not illustrative.** Every file ends with `if __name__ == "__main__":` and prints a labelled walkthrough, so `python 05_functions.py` always produces readable output and exit code 0.
- **Comments explain decisions, not syntax.** Each block answers three questions: what problem does this solve, when should I reach for it, and what is the usual trap.
- **Comments and docstrings are written in Simplified Chinese.** Printed output stays ASCII-only, so the walkthroughs look identical in every console (including Windows code pages such as cp936 and cp1252) and never raise `UnicodeEncodeError` when you redirect them to a file.
- **Annotated.** Function signatures and key variables carry type hints, and the comments say what each hint buys you (and where it is only documentation).
- **Standard library only.** The examples need no third-party package; `pytest`, `mypy` and `ruff` are optional development tools.
- **Portfolio-sized.** Each file is roughly 100–250 lines — long enough to be realistic, short enough to read in one sitting.

What it is **not**: a language reference, a framework, or a complete course. It is a spine of well-commented examples to edit, break and re-run.

## Requirements

| Item                 | Version           | Why                                                                                                                                               |
| -------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Python               | **3.10 or newer** | `match`/`case` (04), `X \| Y` annotations (12), `dataclass(slots=True, kw_only=True)` (09), `zip(strict=True)` (04) and `itertools.pairwise` (07) |
| Runtime dependencies | none              | Every example imports only the standard library                                                                                                   |
| Development tools    | optional          | `pytest`, `mypy`, `ruff` — only for the checks below                                                                                              |

```bash
python --version        # expect Python 3.10.x or newer
```

The examples are written to behave identically on Windows, macOS and Linux: no shell commands, no hard-coded absolute paths, and all printed output is ASCII so it renders the same in every console.

## Quick start

```bash
# 1. get the files
git clone https://github.com/jiejiebiezheyang/pylearn.git
cd pylearn

# 2. create an isolated environment (recommended, not required to run the examples)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. install the optional development tools
python -m pip install -r requirements.txt

# 4. run any example
python 01_variables.py
python 15_concurrency.py
```

Run them all, from the repository root:

```bash
# macOS / Linux
for f in 0*.py 1[0-5]*.py; do python "$f"; done

# Windows PowerShell
Get-ChildItem *.py | Where-Object { $_.Name -ne '16_testing_test.py' } | ForEach-Object { python $_.Name }
```

Run the test file with pytest (it also runs itself through `python 16_testing_test.py`):

```bash
pytest -v 16_testing_test.py
```

## File index

| #   | File                                                     | Topic                                  | Key points                                                                                                                                                                                                                                                       |
| --- | -------------------------------------------------------- | -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01  | [01_variables.py](01_variables.py)                       | Variables, constants, basic types      | dynamic typing is rebinding; `None` and `is None`; `int` is arbitrary precision; float equality traps; truthiness table; `Final` constants; annotations are not enforced; PEP 8 naming                                                                           |
| 02  | [02_strings.py](02_strings.py)                           | Strings, formatting, bytes             | f-string format specs and the `=` debug form; slicing everywhere; `strip`/`split`/`join`/`casefold`; `+` in a loop is O(n²); UTF-8 vs ASCII; `encode`/`decode`, `errors="replace"`; why `encoding=` is never optional                                            |
| 03  | [03_collections.py](03_collections.py)                   | list, tuple, dict, set, comprehensions | mutability; aliasing vs shallow vs deep copy; tuple unpacking and hashability; dict order, `get`, `setdefault`, `\|` merge; set algebra; list/dict/set comprehensions and generator expressions                                                                  |
| 04  | [04_control_flow.py](04_control_flow.py)                 | if, for, while, match/case             | `elif` chains and ternaries; `range`, `enumerate`, `zip(strict=True)`; `for`/`while` … `else`; the walrus operator; structural pattern matching with guards and mapping patterns; never mutate while iterating                                                   |
| 05  | [05_functions.py](05_functions.py)                       | Functions and arguments                | the mutable-default bug and the `None` sentinel; keyword arguments; positional-only (`/`) and keyword-only (`*`) parameters; `*args`/`**kwargs`; functions as values; `lambda` in place, `def` when named; `functools.partial`                                   |
| 06  | [06_scope_closures.py](06_scope_closures.py)             | Scope, closures, decorators            | LEGB lookup order; `global` vs `nonlocal`; closures keep state; the late-binding loop trap; decorators with and without arguments; `functools.wraps`; stacked decorators; `lru_cache`                                                                            |
| 07  | [07_iterators_generators.py](07_iterators_generators.py) | Iterators and generators               | `iter`/`next`/`StopIteration`; a hand-written iterator vs a generator; laziness and one-shot exhaustion; `yield from`; `send`/`close`; `itertools` (`islice`, `chain`, `groupby`, `pairwise`, `product`, `tee`); memory of generator expressions                 |
| 08  | [08_oop.py](08_oop.py)                                   | Classes and objects                    | instance vs class attributes and the shared-mutable trap; `@property` with validation; `@classmethod`/`@staticmethod`; inheritance, `super()` and the MRO; dunder methods (`__repr__`, `__eq__`, `__hash__`, `__len__`, `__getitem__`, `__add__`, `__call__`)    |
| 09  | [09_dataclasses.py](09_dataclasses.py)                   | Data classes and named tuples          | generated `__init__`/`__repr__`/`__eq__`; `field(default_factory=...)`; `frozen`, `order`, `slots`, `kw_only`; `__post_init__` validation with `object.__setattr__`; `asdict`/`astuple`/`replace`; `NamedTuple` and when it beats a dataclass                    |
| 10  | [10_exceptions.py](10_exceptions.py)                     | Exceptions                             | `try`/`except`/`else`/`finally` order; specific handlers first; custom exception hierarchies carrying data; chaining with `raise … from exc`; why bare `except:` is dangerous; `contextlib.suppress`; the `return`-in-`finally` trap; `assert` is not validation |
| 11  | [11_modules_packages.py](11_modules_packages.py)         | Modules, packages, tooling             | the four import forms; `__name__`, `__file__`, `sys.modules`, `sys.path`; loading a file by path (`spec_from_file_location`); package layout, `__init__.py`, relative imports; `python -m` vs `python file.py`; venv, pip, `pyproject.toml`                      |
| 12  | [12_type_annotations.py](12_type_annotations.py)         | Typing and static checking             | builtin generics; `str \| None`; `Literal`, `NewType`, `TypedDict`; `Protocol` for structural typing; `TypeVar` and `@overload`; `Any`/`cast` escape hatches; `TYPE_CHECKING`; what mypy catches that tests do not                                               |
| 13  | [13_stdlib_tour.py](13_stdlib_tour.py)                   | Standard library tour                  | `pathlib` joins, reads, writes, globs and reports metadata; `os` for environment and cwd; `json` dump/load and the types JSON cannot express; aware vs naive `datetime`; `Counter`, `defaultdict`, `deque`; the regex functions worth knowing                    |
| 14  | [14_files_context.py](14_files_context.py)               | Files and context managers             | `with open(...)` and the modes (`w` truncates!); `encoding="utf-8"` and `newline=""`; streaming a file line by line; `seek`/`tell`; `csv` and `json` round trips; a class-based context manager; `@contextmanager` with `try`/`finally`                          |
| 15  | [15_concurrency.py](15_concurrency.py)                   | Concurrency and parallelism            | the GIL in one sentence; a real lost-update race and the lock that fixes it; `queue.Queue` between threads; `multiprocessing` with the `spawn` context and why it needs the `__main__` guard; `asyncio.gather` overlapping waits; a choose-the-tool table        |
| 16  | [16_testing_test.py](16_testing_test.py)                 | Testing and debugging                  | plain `assert` tests; fixtures and per-test isolation; `@pytest.mark.parametrize`; `pytest.raises`/`approx`/`caplog`; built-ins `tmp_path` and `monkeypatch`; a `unittest.TestCase` class in the same run; `pdb` and `logging` workflow notes                    |

## Layout note: why 16 flat files and what `__main__` does

**Why one flat directory works.** These files are _scripts_, not a library. Nothing imports anything else, each filename is unique, and the numbering keeps them ordered in a directory listing. A `src/` package with `__init__.py` files would add import plumbing for zero benefit: you would have to run them as `python -m examples.05_functions`, and `05_functions` is not even a valid module name. Because there is no `__init__.py` here, there is also no chance of an accidental package-level import cycle, and copying a single file out of the repository keeps it fully working.

The rule of thumb: **flat scripts while you learn, a package when something is imported from somewhere else.** The moment a helper is used by two files, move it into `mypkg/helpers.py` with an `__init__.py` and import it (see `11_modules_packages.py` for both layouts).

**What `if __name__ == "__main__":` buys us here.**

- Run the file directly (`python 05_functions.py`) → Python sets `__name__` to `"__main__"` → `main()` runs → you get the walkthrough.
- Import the file (`import 05_functions`, or pytest collecting `16_testing_test.py`) → `__name__` is the module name → `main()` does **not** run → no side effects at import time.
- `multiprocessing` with the `spawn` start method (used by `15_concurrency.py`, and the default on Windows) re-imports the file in every child process. Without the guard, each child would re-run the whole demo, spawn more children, and never finish — this is the single most common Windows-specific multiprocessing bug.

Putting the demos inside functions instead of at module level gives the same protection twice over: imports stay silent, and the code is still testable and readable.

## Verification

Every check runs from the repository root. Copy the block for your platform.

```bash
# macOS / Linux
python -m py_compile *.py                       # syntax of all 16 files
ruff check .                                    # lint (config in pyproject.toml)
mypy .                                          # type check, non-strict (see below)
for f in 0*.py 1[0-5]*.py; do python "$f"; done  # run every example
pytest -v 16_testing_test.py                    # the test file
```

```powershell
# Windows PowerShell
Get-ChildItem *.py | ForEach-Object { python -m py_compile $_.Name }
ruff check .
mypy .
Get-ChildItem *.py | Where-Object { $_.Name -ne '16_testing_test.py' } | ForEach-Object { python $_.Name }
pytest -v 16_testing_test.py
```

### Results

| # | Check                     | Command                                      | Result                                                               |
| - | ------------------------- | -------------------------------------------- | -------------------------------------------------------------------- |
| 1 | Byte-compile all 16 files | `python -m py_compile *.py`                  | ✅ pass — 16/16 files compile, no warnings                           |
| 2 | Lint                      | `ruff check .`                               | ✅ pass — `All checks passed!` (ruff 0.16.9)                         |
| 3 | Type check                | `mypy .`                                     | ✅ pass — `Success: no issues found in 16 source files` (mypy 2.3.1) |
| 4 | Run every example         | `python <file>`, one file at a time (all 16) | ✅ pass — 16/16 exit code 0, no stderr, ASCII-only stdout            |
| 5 | Tests                     | `pytest -v 16_testing_test.py`               | ✅ pass — 20 passed in 0.13s                                         |

Recorded on two environments: CPython 3.14.4 / Linux (ruff 0.16.9, mypy 2.3.1, pytest 9.1.1) and CPython 3.14.3 / Windows (pytest 9.1.1). All five checks passed on both. Everything platform-dependent still differs between runs — process ids, the lost-update count in `15_concurrency.py`, the newline translation and locale encoding reported by `14_files_context.py` (`cp936` on the Windows run), and timings. Results also depend on tool versions, since a much older ruff or mypy may not know the rules and checks used here.

### Type-checking policy

`mypy` runs in its **default, non-strict mode**, configured in `[tool.mypy]` in `pyproject.toml`. That is a deliberate choice, not an oversight:

- Several examples intentionally show dynamic patterns — a module loaded by path is typed `Any` until you declare an interface for it (`11_modules_packages.py`), `# type: ignore[assignment]` demonstrates what the checker rejects (`01_variables.py`), and `12_type_annotations.py` prints mypy's own error messages as teaching material.
- Strict mode (`mypy --strict`) would demand annotations on every parameter, forbid untyped decorators and reject those demonstrations. It is an excellent next step for your own project: run `mypy --strict .` and see how many real issues it finds once the examples are behind you.
- What is already enforced: every public function in every file is annotated, and the configured mode passes cleanly (see the results table above).

## Learning path

Read in order the first time; the later files assume the vocabulary of the earlier ones. A three-pass approach works well:

1. **Run it.** `python 06_scope_closures.py`, read the output, and match each printed line to the code that produced it.
2. **Break it.** Change a value and predict the failure before re-running. Delete the `nonlocal` in `06`, the `functools.wraps` in `06`, or the lock in `15` and watch what happens.
3. **Extend it.** Add a case to the tests in `16_testing_test.py`, or a new variant to the comprehension section of `03_collections.py`.

| Stage                | Files                  | Focus                                                |
| -------------------- | ---------------------- | ---------------------------------------------------- |
| Foundations          | 01 → 02 → 03 → 04      | values, text, containers, control flow               |
| Building blocks      | 05 → 06 → 07 → 08      | functions, scope, laziness, objects                  |
| Structure and safety | 09 → 10 → 12           | data modelling, error handling, types                |
| Real work            | 11 → 13 → 14 → 15 → 16 | imports, standard library, files, concurrency, tests |

Pairs worth comparing side by side: `05` vs `06` (arguments vs closures), `08` vs `09` (hand-written class vs dataclass), `10` vs `14` (errors vs cleanup), `15` vs `16` (races vs the tests that would catch them).

## License

[MIT](LICENSE) © 2026 jiejiebiezheyang
