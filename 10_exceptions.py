"""10 - 异常：try/except/else/finally、自定义类型、异常链。

本文件讲什么
------------
* ``try`` / ``except`` / ``else`` / ``finally``，以及它们的执行顺序。
* 捕获具体类型、捕获整个继承体系，以及为什么 ``except:`` 很糟。
* 携带数据的自定义异常类（错误码、出错的键）。
* 用 ``raise ... from exc`` 和 ``from None`` 做 exception chaining。
* ``contextlib.suppress`` 与 EAFP 风格。

为什么重要
----------
异常用于表达「这个操作无法继续」，而不是普通的条件分支。被捕获后又被
吞掉、或者重新抛出时丢掉原始原因的错误，是生产环境里最难诊断的 bug。
两条规则能让 traceback 保持有用：只捕获你确实能处理的最窄类型；转换
错误时用 ``from exc`` 把原因链上。
"""

import contextlib
from pathlib import Path


class AppError(Exception):
    """应用异常的基类：``except AppError`` 能抓住所有应用层失败。"""

    def __init__(self, message: str, *, code: int = 1) -> None:
        super().__init__(message)  # Exception 会把消息存起来供 str() 使用
        self.code: int = code


class ConfigError(AppError):
    """某一种具体失败。继承让基类捕获依然有效。"""

    def __init__(self, key: str) -> None:
        super().__init__(f"missing configuration key: {key!r}", code=2)
        self.key: str = key


class NetworkError(AppError):
    """有时子类只需要一个名字，以便能被单独捕获。"""


def divide(left: float, right: float) -> float:
    """EAFP：直接做运算，让 Python 报告问题。"""
    return left / right  # right == 0 时抛 ZeroDivisionError


def parse_age(text: str) -> int:
    """把底层错误翻译成领域错误，同时保留原因。"""
    try:
        return int(text)
    except ValueError as exc:
        # ``from exc`` 会记录 __cause__，于是 traceback 同时显示两个错误：
        # "The above exception was the direct cause of the following"。
        raise AppError(f"not a number: {text!r}") from exc


def read_setting(settings: dict[str, str], key: str) -> str:
    """``else`` 只在 try 块成功时执行；try 块要保持尽量小。"""
    try:
        value = settings[key]
    except KeyError as exc:
        raise ConfigError(key) from exc
    else:
        # 这段代码不可能抛 KeyError，因此不会被上面的处理器意外捕获。
        # 这正是 ``else`` 的意义所在。
        return value
    finally:
        # ``finally`` 在任何路径上都会执行：成功、错误已处理、或者异常
        # 继续向上传播。只用它做清理。
        pass


def cleanup_order_demo() -> list[str]:
    """``finally`` 先做清理，随后原异常继续向上传播。"""
    events: list[str] = []
    try:
        events.append("try")
        raise RuntimeError("body failed")
    except RuntimeError as exc:
        events.append(f"except saw {exc!r}")
    finally:
        # 任何路径都会执行：成功、错误已处理，或者异常继续向上传播。
        # 只应该把清理逻辑放在这里。
        events.append("finally")
    events.append("after the try statement")
    return events


def finally_pitfall_note() -> str:
    """把反模式记录下来，同时不触发 SyntaxWarning。

    反模式（千万不要这样写）::

        def broken() -> str:
            try:
                raise RuntimeError("this message disappears")
            finally:
                return "returned from finally"   # ruff/flake8-bugbear B012

    ``finally`` 里的 ``return`` 会丢弃正在传播的异常，于是 ``broken()``
    悄无声息地「成功」了，被它掩盖的 bug 会在很久之后才暴露。Python 3.14
    在编译这类文件时甚至会报 ``SyntaxWarning: 'return' in a 'finally'
    block``。正确做法是在 try 语句「之后」返回，让 ``finally`` 只负责清理。
    """
    return "documented above, never executed"


def describe(error: Exception) -> str:
    """处理器的顺序很重要：第一个匹配的分支胜出。"""
    try:
        raise error
    except ConfigError:
        return "config problem"  # 必须排在 AppError 分支之前
    except AppError:
        return "app problem"
    except (TypeError, ValueError):
        return "data problem"  # 用 tuple 把多个类型合并进一个处理器
    except Exception:
        # 在边界处（main、worker 循环）做日志兜底捕获。这里捕获
        # Exception 是有意为之；裸 ``except:`` 还会吞掉 KeyboardInterrupt
        # 和 SystemExit，而这两个必须保持可中断。
        return "unexpected problem"


def ordering_demo() -> None:
    """打印 try -> except/else -> finally 的确切顺序。"""

    def attempt(fail: bool) -> str:
        try:
            print("   try")
            if fail:
                raise ValueError("boom")
        except ValueError:
            print("   except")
            return "recovered"
        else:
            print("   else (no exception)")
            return "ok"
        finally:
            print("   finally (always)")

    print("success path:", attempt(False))
    print("failure path:", attempt(True))


def suppress_demo() -> None:
    """``contextlib.suppress`` 用来声明「这个失败可以接受」。"""
    optional = Path("__no_such_file__.txt")
    with contextlib.suppress(FileNotFoundError):
        optional.read_text(encoding="utf-8")
    print("suppressed   : missing optional file is not an error")

    # 坑：绝不要在不属于你的代码外面宽泛地 suppress（``suppress(Exception)``）；
    # 那会把真实 bug 藏起来，比如属性名拼错。


def main() -> None:
    """按易读的顺序跑完所有演示。"""
    print("== basics ==")
    print("divide(10, 4):", divide(10, 4))
    try:
        divide(1, 0)
    except ZeroDivisionError as exc:
        print("caught      :", type(exc).__name__, "-", exc)

    print("\n== custom exceptions + chaining ==")
    try:
        parse_age("abc")
    except AppError as exc:
        print("message     :", exc)
        print("code        :", exc.code, "| cause:", type(exc.__cause__).__name__)
    print("valid age   :", parse_age("42"))

    try:
        read_setting({}, "timeout")
    except ConfigError as exc:
        print("key         :", exc.key, "| is AppError:",
              isinstance(exc, AppError))

    print("\n== handler order ==")
    for error in (ConfigError("x"), NetworkError("down"), TypeError("bad type"),
                  RuntimeError("other")):
        print(f"  {type(error).__name__:<12} ->", describe(error))

    print("\n== try/except/else/finally order ==")
    ordering_demo()

    print("\n== pitfalls ==")
    print("cleanup order:", cleanup_order_demo())
    print("finally trap :", finally_pitfall_note())
    suppress_demo()

    # 还有两个值得记住的陷阱：
    # * 不带参数的 ``raise SomeError`` 会重新抛出「当前活跃」的异常；在
    #   ``except`` 块里这正是你要的，在块外则会抛 RuntimeError
    #   ("No active exception to re-raise")。
    # * ``assert`` 会被 ``python -O`` 移除，所以它只用于检查程序员自己的
    #   失误，绝不要用来校验用户输入。
    try:
        assert 1 == 2, "assertions document invariants"
    except AssertionError as exc:
        print("AssertionError:", exc)


if __name__ == "__main__":
    main()
