"""16 - 测试与调试：pytest、fixture、parametrize、unittest、logging。

如何运行本文件
--------------
    pytest -v 16_testing_test.py      # 常规方式
    python 16_testing_test.py         # 也可以：__main__ 会调用 pytest

本文件讲什么
------------
* 朴素的 ``assert`` 测试，以及 pytest 为什么不需要样板代码。
* Fixture：多个测试共享的准备代码，且每个测试都拿到全新的实例。
* ``@pytest.mark.parametrize``：一个测试体，报告成多个用例。
* ``pytest.raises``、``pytest.approx`` 与 ``caplog``。
* 内置 fixture：``tmp_path``（文件）与 ``monkeypatch``（环境变量）。
* 一个 ``unittest.TestCase`` 类，由同一次运行收集。
* 测试失败时 ``pdb`` 和 ``logging`` 各在哪里发挥作用。

为什么重要
----------
测试套件是唯一能告诉你"某次改动弄坏了你没想到的东西"的工具。pytest 小
到可以一口气读完：名为 ``test_*`` 的函数会被收集，普通 ``assert`` 语句
会被改写以显示真实取值，而 fixture 同时取代了 ``setUp``/``tearDown`` 和
大部分 mock。调试从失败报告处开始：``-x`` 在第一个失败处停下，
``--pdb`` 带着仍然存活的局部变量把你丢进调试器。
"""

import logging
import os
import unittest
from dataclasses import dataclass
from pathlib import Path

import pytest


def add(left: int, right: int) -> int:
    """最简单被测单元：纯输入 -> 输出。"""
    return left + right


def divide(left: float, right: float) -> float:
    """抛异常而不是返回一个神奇的哨兵值，这样测试才能断言它。"""
    if right == 0:
        raise ZeroDivisionError("division by zero")
    return left / right


@dataclass
class Account:
    """有状态的代码需要准备代码；这正是 fixture 的用途。"""

    owner: str
    balance: float = 0.0

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount


@pytest.fixture
def account() -> Account:
    """每个测试一个全新的 Account。function 作用域是默认值，也最安全：
    没有任何测试能给别的测试留下状态。"""
    return Account("ada", 100.0)


@pytest.fixture
def note_file(tmp_path: Path) -> Path:
    """``tmp_path`` 是内置 fixture：每个测试一个新临时目录（会自动删除），
    所以测试从不碰真实文件系统。"""
    note = tmp_path / "notes.txt"
    note.write_text("hello\n", encoding="utf-8")
    return note


@pytest.fixture
def app_user(monkeypatch: pytest.MonkeyPatch) -> str:
    """``monkeypatch`` 修改环境变量，并自动撤销改动。"""
    monkeypatch.setenv("APP_USER", "ada")
    return os.environ["APP_USER"]


def test_add() -> None:
    """尽可能小的测试：调用代码，断言结果。"""
    assert add(2, 3) == 5


def test_add_is_commutative() -> None:
    assert add(2, 3) == add(3, 2)


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (1, 2, 3),
        (0, 0, 0),
        (-1, 1, 0),
        (10**6, 1, 10**6 + 1),
    ],
)
def test_add_table(left: int, right: int, expected: int) -> None:
    """一个测试体，四个上报用例：失败信息会点明具体输入。"""
    assert add(left, right) == expected


def test_divide() -> None:
    assert divide(6, 3) == pytest.approx(2.0)


def test_divide_by_zero() -> None:
    """``pytest.raises`` 在没抛异常时判定测试失败。"""
    with pytest.raises(ZeroDivisionError, match="division by zero"):
        divide(1, 0)


def test_float_comparison() -> None:
    """浮点数直接判等是个陷阱；pytest.approx 是解药。"""
    assert 0.1 + 0.2 != 0.3
    assert 0.1 + 0.2 == pytest.approx(0.3)
    assert 0.1 + 0.2 == pytest.approx(0.3, abs=1e-9)


def test_balance_after_deposit(account: Account) -> None:
    account.deposit(50.0)
    assert account.balance == pytest.approx(150.0)


def test_balance_after_withdraw(account: Account) -> None:
    account.withdraw(40.0)
    assert account.balance == pytest.approx(60.0)


def test_withdraw_too_much(account: Account) -> None:
    with pytest.raises(ValueError, match="insufficient funds"):
        account.withdraw(999.0)


def test_fixture_is_fresh(account: Account) -> None:
    """fixture 为这个测试又跑了一次，所以余额没被动过。"""
    assert account.balance == pytest.approx(100.0)


def test_bad_argument_raises(account: Account) -> None:
    with pytest.raises(ValueError, match="must be positive"):
        account.deposit(0.0)


def test_note_file(note_file: Path) -> None:
    assert note_file.read_text(encoding="utf-8").strip() == "hello"
    assert note_file.is_file()


def test_environment_fixture(app_user: str) -> None:
    assert app_user == "ada"


def test_logging_is_testable(caplog: pytest.LogCaptureFixture) -> None:
    """``caplog`` 捕获日志记录，所以 logging 同样可以被断言。"""
    with caplog.at_level(logging.WARNING):
        logging.getLogger("demo").warning("disk almost full")
    assert "disk almost full" in caplog.text
    assert caplog.records[-1].levelname == "WARNING"


class TestAccountUnittest(unittest.TestCase):
    """pytest 也会运行 unittest.TestCase 类，所以老测试套件可以逐步迁移。
    新测试优先用普通函数：fixture 比 setUp/tearDown 继承更清晰。"""

    def setUp(self) -> None:
        self.account = Account("bob", 10.0)

    def test_deposit(self) -> None:
        self.account.deposit(5.0)
        self.assertEqual(self.account.balance, 15.0)

    def test_withdraw_floor(self) -> None:
        with self.assertRaises(ValueError):
            self.account.withdraw(11.0)


def test_debugging_tools_are_documented() -> None:
    """把调试工作流写成文档，而不是让测试套件停下来等人。

    调试配方：运行 ``pytest -x --pdb`` 在第一个失败处停下，此时 traceback
    和局部变量都还在；在 pdb 里用 ``n``（next）、``s``（step）、
    ``c``（continue）、``p expr``（print）、``w``（where）和 ``q``（quit）。
    对脚本而言，``breakpoint()``（Python 3.7+）不用 import pdb 就能做到
    同样的事。
    """
    notes: tuple[str, ...] = (
        "logging.getLogger(__name__) in every module; print() for throwaway",
        "log levels: DEBUG < INFO < WARNING < ERROR < CRITICAL",
        "pytest -x     stop at the first failure",
        "pytest -k add select tests whose name contains 'add'",
        "pytest --lf   re-run only the tests that failed last time",
        "pytest -q     less output; -v more; -s show prints",
    )
    assert notes
    assert all(isinstance(note, str) and note for note in notes)


if __name__ == "__main__":
    # 直接运行本文件同样会通过 pytest 跑完整个测试套件，所以每个测试都
    # 通过时 ``python 16_testing_test.py`` 退出码为 0。
    raise SystemExit(pytest.main([__file__, "-v"]))
