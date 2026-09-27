"""05 - 函数：参数、keyword-only 参数、*args/**kwargs、一等函数。

本文件讲什么
------------
* 默认值，以及为什么可变默认值是一个 bug。
* 关键字参数、keyword-only（``*``）参数和 positional-only（``/``）参数。
* ``*args`` 与 ``**kwargs``：收集并转发任意参数。
* 函数作为值：传递、返回、放进 list 里保存。
* 什么时候用 ``lambda``，什么时候用更合适的 ``functools.partial``。

为什么重要
----------
签名就是 API。把参数标成 keyword-only，可以防止调用方把两个同类型的值写反；
``/`` 则让某个公开的名字在后面还能自由改名。下面的可变默认值陷阱是 Python
经典面试题，因为它会在多次调用之间悄悄共享状态。
"""

import inspect
from collections.abc import Callable, Iterable
from functools import partial
from typing import Any

# 类型别名让冗长的标注变得好读。``Callable[[int], int]`` 表示「接收一个 int、
# 返回一个 int 的函数」；``...`` 表示「参数任意」。
IntTransform = Callable[[int], int]


def greet(name: str, greeting: str = "Hello", punctuation: str = "!") -> str:
    """默认值只在 ``def`` 执行时求值一次，之后被所有调用共享。"""
    return f"{greeting}, {name}{punctuation}"


def append_item(item: str, bucket: list[str] | None = None) -> list[str]:
    """真正的默认值必须每次新建时，就用 ``None`` 当哨兵值。"""
    if bucket is None:  # 每次调用新建一个 list，而不是共用一个 list
        bucket = []
    bucket.append(item)
    return bucket


def broken_append_item(item: str, bucket: list[str] = []) -> list[str]:  # noqa: B006
    """保留下来作反例：默认的那个 list 只创建一次。

    每次调用都往*同一个* list 里追加，于是函数会在多次调用之间泄漏状态。
    开启 B 类规则时，ruff 会把它标为 B006。
    """
    bucket.append(item)
    return bucket


def flexible(first: int, /, second: int, *, scale: int = 1) -> int:
    """``/`` 标记 positional-only 参数；``*`` 标记 keyword-only 参数。

    ``first`` 不能用 ``first=...`` 传（所以以后改名不会破坏调用方）。
    ``scale`` 必须以 ``scale=3`` 的形式传（调用方不可能把它的位置误当成
    ``second``）。
    """
    return (first + second) * scale


def collect(*args: int, **options: object) -> tuple[int, dict[str, object]]:
    """``*args`` 会变成 tuple，``**options`` 会变成 dict。"""
    return sum(args), dict(options)


def forward(*args: Any, **kwargs: Any) -> str:
    """包装函数用 ``*`` 和 ``**`` 把收到的参数原样转发出去。"""
    name = kwargs.pop("name", "anonymous")
    return f"{name}: args={args} kwargs={sorted(kwargs)}"


def apply_all(value: int, transforms: Iterable[IntTransform]) -> int:
    """把函数当数据来用；这就是「一等」给你带来的好处。"""
    result: int = value
    for transform in transforms:
        result = transform(result)
    return result


def make_multiplier(factor: int) -> IntTransform:
    """返回一个新函数；返回的 closure 记住了 ``factor``。"""

    def multiply(value: int) -> int:
        return value * factor

    return multiply


def first_class_demo() -> None:
    """函数也是对象：可以赋值、传递、保存，也可以反射查看。"""
    doubler: IntTransform = make_multiplier(2)
    tripler: IntTransform = make_multiplier(3)
    print("doubler(21) :", doubler(21))
    print("pipeline    :", apply_all(2, [doubler, tripler]))
    # 闭包保留了返回函数的签名信息（`inspect.signature` 可以读出来），这比直接
    # 访问 `__name__`/`__code__` 更稳，类型检查器也完全认可。
    print("signature   :", inspect.signature(doubler))

    # 内置函数同样是函数，所以按某个辅助函数排序不需要任何特殊处理。
    words: list[str] = ["bb", "a", "ccc"]
    print("sorted by len:", sorted(words, key=len))

    # ``lambda`` 只是「一个只用一次的小函数」的表达式写法。
    # 坑：``square = lambda x: x * x`` 会被 ruff（E731）和所有 review 的人挑刺；
    # 应该写成 ``def square(x): ...``，它在 traceback 里还有真正的函数名。
    print("lambda inline:", sorted(words, key=lambda word: word[-1]))

    # 当你需要的是一个普通可调用对象、又不想写 lambda 函数体（比如交给
    # map() 或注册成回调）时，用 ``partial`` 冻结参数。
    add_ten = partial(flexible, 10, 1, scale=1)
    print("partial     :", add_ten())


def main() -> None:
    """按易读的顺序跑完所有示例。"""
    print("== defaults ==")
    print(greet("Ada"))
    print(greet("Ada", "Hi"))
    print(greet("Ada", punctuation="?"))  # 关键字参数，与位置无关
    print("fresh default:", append_item("a"), append_item("b"))
    print("shared default (bug):", broken_append_item("a"), broken_append_item("b"))

    print("\n== positional-only / keyword-only ==")
    print(flexible(1, 2, scale=10))
    print(flexible(1, second=2))  # 调用点可读：不用去猜位置
    # flexible(first=1, second=2)          # TypeError：positional-only
    # flexible(1, 2, 10)                   # TypeError：keyword-only

    print("\n== *args / **kwargs ==")
    total, options = collect(1, 2, 3, verbose=True, retries=2)
    print("total       :", total, "| options:", options)
    print("forward     :", forward(1, 2, name="ada", dry_run=True))

    print("\n== first-class functions ==")
    first_class_demo()
    # 坑：每个函数都有 ``__doc__``。缺失 docstring 时它是 None，help() 也就
    # 显示不出有用信息；每个公开函数至少留一行说明。


if __name__ == "__main__":
    main()
