"""09 - Data classes 与 named tuple。

本文件讲什么
------------
* ``@dataclass``：根据注解生成 __init__、__repr__ 和 __eq__。
* ``field(default_factory=...)`` 处理可变默认值，另有 ``repr``/``compare``。
* ``frozen=True``（不可变且可哈希）、``order=True``、``slots=True``、
  ``kw_only=True``（Python 3.10 上全部可用）。
* 用 ``__post_init__`` 做校验和规范化。
* ``typing.NamedTuple``：既是 tuple，又带具名字段。

为什么重要
----------
大多数类不过是「几个字段加上相等性判断」，而手写这些代码正是复制粘贴
错误的温床。dataclass 用你本来就要写的注解把它生成出来，注解因此获得
了双重作用。当值必须保持真正的 tuple（可解包、可索引、可作 JSON 数组、
零额外开销存储）时，NamedTuple 是更轻量的选择。
"""

import math
from dataclasses import asdict, astuple, dataclass, field, replace
from typing import Any, NamedTuple


@dataclass
class Point:
    """由注解生成：__init__、__repr__ 和 __eq__。

    ``x`` 和 ``y`` 没有默认值，因此必须按位置传入。
    ``label`` 有默认值，而 Python 要求带默认值的字段排在最后，
    否则生成出来的 __init__ 签名会有歧义。
    """

    x: float
    y: float
    label: str = "unnamed"

    def distance_to_origin(self) -> float:
        """行为仍然是普通方法；dataclass 并不是只能装数据。"""
        return math.hypot(self.x, self.y)


@dataclass
class Basket:
    """可变默认值必须写成 ``field(default_factory=...)``。"""

    owner: str
    # 坑：写成 ``items: list[str] = []`` 会在创建类时就抛 ValueError，
    # 因为所有 Basket 会共享同一个 list（05_functions.py 里的可变默认值
    # 陷阱）。default_factory 会为每个实例调用一次 list()。
    items: list[str] = field(default_factory=list)
    discount: float = field(default=0.0, repr=False, compare=False)

    def total(self, prices: dict[str, float]) -> float:
        """``compare=False`` 也让 discount 不参与 __eq__。"""
        gross = sum(prices.get(item, 0.0) for item in self.items)
        return gross * (1.0 - self.discount)


@dataclass(frozen=True, order=True, slots=True)
class Version:
    """frozen = 不可变且可哈希；order = 可排序；slots = 没有 __dict__。"""

    major: int
    minor: int = 0

    @property
    def label(self) -> str:
        return f"{self.major}.{self.minor}"


@dataclass(frozen=True)
class Email:
    """``__post_init__`` 在 __init__ 之后立刻做校验和规范化。"""

    address: str
    verified: bool = False

    def __post_init__(self) -> None:
        if "@" not in self.address:
            raise ValueError(f"invalid address: {self.address!r}")
        cleaned = self.address.strip().lower()
        # 坑：frozen=True 时直接写 ``self.address = cleaned`` 会抛
        # FrozenInstanceError。需要规范化时改用 object.__setattr__。
        if cleaned != self.address:
            object.__setattr__(self, "address", cleaned)


@dataclass(kw_only=True)
class Config:
    """``kw_only=True`` 强制使用 ``host=...`` 的调用形式，可读性更好，
    而且以后新增字段不会破坏现有调用。"""

    host: str
    port: int = 8080
    debug: bool = False


@dataclass
class Timestamped:
    created_at: str


@dataclass
class Record(Timestamped):
    """字段按基类优先的顺序合并；带默认值的字段必须留在最后。

    坑：如果 ``Timestamped.created_at`` 有默认值而 ``payload`` 没有，
    生成的 __init__ 就是非法的，Python 会抛出
    ``TypeError: non-default argument 'payload' follows default argument``。
    """

    payload: str = ""


class Coordinate(NamedTuple):
    """NamedTuple 本身就是 tuple：可迭代、可索引、可解包、可哈希。"""

    latitude: float
    longitude: float = 0.0

    def as_text(self) -> str:
        return f"{self.latitude:.3f},{self.longitude:.3f}"


def dataclass_demo() -> None:
    """生成的方法、辅助函数，以及值语义。"""
    point = Point(3.0, 4.0)
    print("repr         :", point)
    print("eq by value  :", point == Point(3.0, 4.0), "| is identity:",
          point is Point(3.0, 4.0))
    print("method       :", point.distance_to_origin())
    print("asdict       :", asdict(point))
    print("astuple      :", astuple(point))
    print("replace      :", replace(point, label="custom"))
    print("has __dict__ :", hasattr(point, "__dict__"))
    # 坑：@dataclass 生成的 __eq__ 会把 __hash__ 置为 None，除非
    # frozen=True（或 eq=False），所以默认情况下实例不可哈希。


def field_demo() -> None:
    """default_factory、repr=False 和 compare=False 的实际效果。"""
    first = Basket("ada")
    second = Basket("bob")
    first.items.append("apple")
    print("no sharing   :", first.items, second.items)

    prices: dict[str, float] = {"apple": 2.0}
    print("total        :", first.total(prices))
    cheap = Basket("ada", ["apple"], discount=0.5)
    print("repr hides discount:", cheap)
    print("compare ignores it :", cheap == first)
    # 坑：两个对象折扣不同却比较相等。字段若承载真实语义，就保留
    # compare=True（默认值）。


def frozen_demo() -> None:
    """不可变性、哈希和排序。"""
    versions = [Version(1, 2), Version(1, 0), Version(2)]
    print("sorted       :", sorted(versions))
    print("labels       :", [version.label for version in versions])
    print("hashable set :", len({Version(1, 0), Version(1, 0)}))
    print("slots        :", hasattr(Version(1, 0), "__dict__"))
    try:
        # mypy 在你运行之前就会拒绝这一行，运行时 dataclass 会抛
        # FrozenInstanceError。
        Version(1, 0).minor = 5  # type: ignore[misc]
    except Exception as exc:  # FrozenInstanceError 是 AttributeError 的子类
        print("frozen guard :", type(exc).__name__)


def validation_demo() -> None:
    """__post_init__ 的校验与规范化。"""
    try:
        Email("not-an-address")
    except ValueError as exc:
        print("rejected     :", exc)
    print("normalised   :", Email("  Ada@Example.COM  "))
    print("verified flag:", Email("ada@example.com", True).verified)


def namedtuple_demo() -> None:
    """NamedTuple 保留 tuple 行为，同时加上字段名。"""
    place = Coordinate(51.5, -0.12)
    print("repr         :", place)
    print("by name/index:", place.latitude, place[0])
    print("unpacking    :", "{:.1f} / {:.1f}".format(*place))
    print("is a tuple   :", isinstance(place, tuple), "| hashable:",
          len({place, Coordinate(51.5, -0.12)}))
    print("_replace     :", place._replace(longitude=0.0))
    print("method       :", place.as_text())
    # 坑：NamedTuple 不可变，``_replace`` 返回的是新对象。字段多、
    # 可选字段多的大记录用带默认值的 dataclass 更顺手；小而定型的记录
    # 用 NamedTuple，省内存，而且能用在任何接受 tuple 的地方。


def main() -> None:
    """按易读的顺序跑完所有演示。"""
    print("== dataclass basics ==")
    dataclass_demo()
    print("\n== field() ==")
    field_demo()
    print("\n== frozen / order / slots ==")
    frozen_demo()
    print("\n== validation ==")
    validation_demo()
    print("\n== NamedTuple ==")
    namedtuple_demo()

    print("\n== inheritance and kw_only ==")
    print("merged fields:", Record("2026-01-01", "payload"))
    print("kw_only      :", Config(host="localhost", port=5432))
    data: dict[str, Any] = asdict(Config(host="db"))
    print("asdict works :", sorted(data))


if __name__ == "__main__":
    main()
