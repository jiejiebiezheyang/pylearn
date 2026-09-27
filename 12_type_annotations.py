"""12 - 类型注解与 mypy 静态检查。

本文件讲什么
------------
* 函数和变量上的注解：内置泛型、``|`` 联合类型。
* ``Literal``、``NewType``、``TypedDict`` 和 ``Protocol``。
* 用 ``TypeVar`` 表达「进出同一种类型」，用 ``@overload`` 做分派。
* ``Any`` 与 ``cast``：逃生舱口，以及它们的代价。
* ``TYPE_CHECKING``：只给类型检查器看的导入。
* 如何运行 mypy，以及它能抓到哪些测试抓不到的问题。

为什么重要
----------
测试只检查你想到的那些取值；类型检查器会走遍你写下的每一条分支。运行时
注解依然是可选的，所以可以逐步添加、零成本：先从函数签名开始，把 mypy
当作第二位评审。README 解释了本项目为什么以默认（非严格）模式运行
mypy：这些示例刻意展示了动态用法，严格模式会对其报错，尽管它们是正确的。
"""

from collections.abc import Callable, Iterable, Sequence
from typing import TYPE_CHECKING, Any, Literal, NewType, Protocol, TypedDict, TypeVar, overload

if TYPE_CHECKING:
    # 只对类型检查器生效；解释器从不会真的导入它。
    # 把重型或循环依赖的导入放在这里，能保持启动速度。
    from decimal import Decimal


def total_of(values: Sequence[float]) -> float:
    """``Sequence`` 同时接受 list、tuple 和 str；写成 ``list`` 就不行。"""
    return sum(values)


def index_by_name(rows: Iterable[str]) -> dict[str, int]:
    """``Iterable`` 是最宽松的可用参数类型；只遍历一次时优先用它。
    返回类型保持具体，调用方才知道自己拿到什么。"""
    return {row: position for position, row in enumerate(rows)}


def apply(func: Callable[[int], int], value: int) -> int:
    """``Callable[[int], int]`` 描述了函数参数应有的形状。"""
    return func(value)


def first_word(text: str | None) -> str:
    """``str | None``（3.10+）是 Optional[str] 的现代写法。"""
    if text is None:  # 这个检查之后 mypy 会把类型收窄为 ``str``
        return ""
    parts = text.split()
    return parts[0] if parts else ""


Mode = Literal["r", "w", "a"]  # 类型别名：mypy 只接受这几个取值


def describe_mode(mode: Mode) -> str:
    """``Literal`` 能在检查期抓住 "read" 这类拼写错误，而不是等到运行时。"""
    names: dict[Mode, str] = {"r": "read", "w": "write", "a": "append"}
    return names[mode]


UserId = NewType("UserId", int)  # 运行时零开销：它本来就是 int


def banner(user_id: UserId) -> str:
    """``NewType`` 阻止你把随便一个 int 当作 user id 传进来。"""
    return f"user #{user_id}"


class Movie(TypedDict):
    """``TypedDict`` 给普通 dict 加上类型：运行时对象仍然是一个 dict。"""

    title: str
    year: int
    rating: float


class HasArea(Protocol):
    """结构化类型（「受检查的鸭子类型」）：不需要继承关系。"""

    def area(self) -> float: ...


class Rect:
    """靠形状匹配 HasArea，并不继承它。"""

    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height


def total_area(shapes: Iterable[HasArea]) -> float:
    """任何带 ``area() -> float`` 的对象都能被接受，即使来自第三方库。"""
    return sum(shape.area() for shape in shapes)


T = TypeVar("T")  # 「某种类型，在这次调用里到处都必须是同一种」


def first_or_default(items: Sequence[T], default: T) -> T:
    """没有 TypeVar 的话，返回类型会退化成 object 或 Any。"""
    return items[0] if items else default


@overload
def label(name: str) -> str: ...
@overload
def label(name: str, count: int) -> str: ...


def label(name: str, count: int | None = None) -> str:
    """实现放在最后；上面两个存根才是调用方看到的东西。

    坑：当各个 overload 必须返回「不同类型」时，mypy 会拒绝把实现标注
    成它们的联合类型（报 "cannot produce return type of signature 1"）。
    官方给出的变通做法是把实现的返回类型标注为 Any。
    """
    return name if count is None else f"{name} x{count}"


def pick(payload: dict[str, Any], key: str) -> str:
    """``Any`` 会关闭对该值的检查；把它限制在边界上。"""
    value: Any = payload[key]
    # ``cast(str, value)`` 是同一件事的显式写法：它只是把你相信的东西
    # 告诉检查器，运行时并不做转换。
    return value


def format_money(amount: "Decimal") -> str:
    """注解写成字符串，于是 Decimal 的导入只对检查器可见。"""
    return f"{amount:.2f}"


def annotations_demo() -> None:
    """用满足类型检查器的取值去调用每个带注解的函数。"""
    print("total_of     :", total_of([1.5, 2.5]))
    print("index_by_name:", index_by_name(["a", "b"]))
    print("apply        :", apply(lambda n: n * 3, 7))
    print("first_word   :", repr(first_word(None)), repr(first_word("hi there")))
    print("describe_mode:", describe_mode("w"))
    print("banner       :", banner(UserId(7)))
    print("total_area   :", total_area([Rect(2.0, 3.0)]))
    print("first_or_def :", first_or_default([1, 2], 0), first_or_default([], "z"))
    print("label        :", label("row"), label("row", 3))
    print("pick         :", pick({"name": "ada"}, "name"))
    # TypedDict 在运行时就是一个普通 dict，这里的键来自数据本身。
    movie: Movie = {"title": "Alien", "year": 1979, "rating": 8.5}
    print("typed dict   :", sorted(movie), "| runtime type:", type(movie).__name__)


def mypy_demo() -> None:
    """打印 mypy 会拒绝的写法，但不真的运行那些代码。"""
    examples: tuple[tuple[str, str], ...] = (
        ('value: int = "text"', "Incompatible types in assignment"),
        ("total_of(['a'])", 'Argument 1 has incompatible type "list[str]"'),
        ("first_word()", "Missing positional argument"),
        ("describe_mode('read')", 'Argument 1 has incompatible type "str"'),
        ("banner(7)", 'Argument 1 has incompatible type "int"; expected "UserId"'),
        (
            "total_area([object()])",
            'Argument 1 has incompatible type "list[object]"',
        ),
        ("label()", "Missing positional argument"),
    )
    print(f"{'rejected code':<28}why mypy refuses it")
    for code, reason in examples:
        print(f"{code:<28}{reason}")

    print()
    print("run the checker with : mypy .            (config: pyproject.toml)")
    print("strictness           : non-strict on purpose; see README.md")
    print("other checkers       : pyright, pyre; all read the same annotations")
    # 坑：注解在运行时不会被校验。``x: int = "s"`` 会一直正常运行，直到
    # 某处拿它做算术——这正是值得在 CI 里多跑一步 mypy 的原因。
    # 坑：不要到处撒 ``# type: ignore`` 来让 mypy 闭嘴；每一个都掩盖了
    # 一种真实可能。请写上错误码（``# type: ignore[arg-type]``），这样
    # 无关的错误仍然会被报出来。


def main() -> None:
    """按易读的顺序跑完所有演示。"""
    print("== annotations in use ==")
    annotations_demo()
    print("\n== what mypy rejects ==")
    mypy_demo()


if __name__ == "__main__":
    main()
