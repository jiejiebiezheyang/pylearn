"""06 - 作用域、closure 与 decorator。

本文件讲什么
------------
* LEGB：Python 解析一个名字时的查找顺序。
* ``global`` 与 ``nonlocal``：什么时候赋值需要声明。
* Closure：记住外层变量的嵌套函数。
* Decorator：不改函数体就能包装一个函数。
* ``functools.wraps``、``functools.lru_cache``，以及叠加的 decorator。

为什么重要
----------
作用域规则解释了大多数「这里为什么是 None / 我的变量为什么没变」的困惑。
Decorator 是添加横切关注点（日志、计时、重试、缓存、权限）的标准做法，在
各种框架里到处都是，所以认出那三层结构很快就能回本。
"""

import functools
import inspect
from collections.abc import Callable
from typing import Any

# 模块级名字就是 LEGB 里的 "G"。它们在整个进程生命周期内都存在。
GLOBAL_SETTING: str = "prod"
total_calls: int = 0
call_log: list[str] = []


def legb_demo() -> None:
    """Local -> Enclosing -> Global -> Builtins。"""
    where: str = "local value"

    def inner() -> None:
        # ``where`` 不是 inner 的局部变量，所以 Python 在外层函数里找到它
        # （也就是 E）。``GLOBAL_SETTING`` 在模块层找到（G）。
        print("  inner sees :", where, "| global:", GLOBAL_SETTING)

    inner()
    print("  builtin    :", len("abc"))  # len 在 Builtins 里查找（B）


def bump_total() -> None:
    """要给模块级名字赋值，就需要 ``global``。"""
    global total_calls
    total_calls += 1  # 没有 ``global`` 的话，这里会变成全新的局部变量


def read_total() -> int:
    """读取全局名字完全不需要任何声明。"""
    return total_calls


def make_counter(start: int = 0) -> Callable[[], int]:
    """返回一个 closure：不用 class 也能保存状态。"""

    count: int = start

    def counter() -> int:
        # ``nonlocal`` 指向最近的外层函数作用域。没有它的话，
        # ``count += 1`` 会抛 UnboundLocalError（ruff F823 把这种错误标为
        # "local variable referenced before assignment"）。
        nonlocal count
        count += 1
        return count

    return counter


def late_binding_demo() -> None:
    """Closure 捕获的是*变量*，而不是定义那一刻的值。"""
    # 坑：三个 lambda 共用同一个 ``n``，看到的是它的最终值（2）。
    late: list[Callable[[], int]] = [lambda: n for n in range(3)]

    # 修法一：用工厂函数把「当前取值」变成该次调用的参数，每个闭包各有
    # 自己的 ``value``。类型检查器也最喜欢这种写法。
    def bind(value: int) -> Callable[[], int]:
        return lambda: value

    early: list[Callable[[], int]] = [bind(n) for n in range(3)]
    print("late bound (all 2):", [func() for func in late])
    print("early bound       :", [func() for func in early])
    # 修法二（同样常见）：``lambda n=n: n`` 用默认参数绑定当前值。运行时
    # 完全正确，但 mypy 无法推断这种默认参数的类型，会报
    # "Cannot infer type of lambda"；两者都值得知道。


def _name_of(func: Callable[..., Any]) -> str:
    """取函数名：``Callable`` 类型并不保证带有 ``__name__`` 属性，用 getattr 更稳妥。"""
    return str(getattr(func, "__name__", "function"))


def logged(func: Callable[..., Any]) -> Callable[..., Any]:
    """不带参数的 decorator：接收一个函数，返回一个新函数。"""

    # functools.wraps 复制 __name__、__doc__、__module__ 并设置
    # __wrapped__。没有它，help() 和 traceback 只会显示 "wrapper"，
    # 而按 __name__ 分发的框架也会出错。
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        call_log.append(_name_of(func))
        return func(*args, **kwargs)

    return wrapper


def repeat(times: int) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """带参数的 decorator：多一层函数，由它返回真正的 decorator。"""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result: Any = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


@logged
def add(left: int, right: int) -> int:
    """把两个整数相加。"""
    return left + right


@repeat(times=2)
def announce(text: str) -> str:
    """把一条消息打印两次（因为 @repeat）。"""
    print("   announce:", text)
    return text


# Decorator 自下而上生效：logged(repeat(2)(shout))。因此打印顺序是
# "logged" 一次，函数体两次。
@logged
@repeat(times=2)
def shout(text: str) -> str:
    """把一条大写消息打印两次。"""
    print("   SHOUT:", text.upper())
    return text.upper()


@functools.lru_cache(maxsize=None)
def slow_square(number: int) -> int:
    """一行实现 memoisation：同样的输入绝不重复计算。"""
    print("   computing", number)
    return number * number


def decorator_demo() -> None:
    """展示被包装后的函数，以及状态是怎么共享的。"""
    print("add(2, 3)   :", add(2, 3))
    # functools.wraps 会把 __name__、__doc__、__module__ 复制到包装函数上，并把
    # __wrapped__ 指向原函数；inspect 读到的就是这些元数据。
    print("signature   :", inspect.signature(add))
    print("has doc     :", bool(inspect.getdoc(add)))
    print("announce    :", announce("once"))
    print("shout       :", shout("hi"))
    print("call log    :", call_log)

    print("cache miss  :", slow_square(4))
    print("cache hit   :", slow_square(4))
    print("cache info  :", slow_square.cache_info())
    # 坑：maxsize=None 时 lru_cache 会永久保留每个 key 和结果的引用，而且它
    # 要求参数可哈希（不能是 list、不能是 dict）。它还按进程缓存，这在
    # multiprocessing 场景下很重要。


def main() -> None:
    """按易读的顺序跑完所有示例。"""
    print("== LEGB ==")
    legb_demo()

    print("\n== global ==")
    bump_total()
    bump_total()
    print("total_calls :", read_total())
    # 坑：优先把值传进去、再返回出来。``global`` 是给计数器和配置用的，
    # 不是给日常数据流用的。

    print("\n== nonlocal / closures ==")
    counter = make_counter(10)
    print("counter     :", counter(), counter(), counter())
    another = make_counter()
    print("independent :", another())  # 每个 closure 持有自己的状态

    print("\n== late binding ==")
    late_binding_demo()

    print("\n== decorators ==")
    decorator_demo()


if __name__ == "__main__":
    main()
