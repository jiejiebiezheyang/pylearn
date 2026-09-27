"""08 - 面向对象 Python：class、继承、property、dunder 方法。

本文件讲什么
------------
* 一个带有 ``__init__``、实例属性和类属性的 class。
* 共享可变类属性的陷阱，以及属性查找是怎么进行的。
* 用 ``@property`` 实现带校验的计算属性，以及 ``@classmethod`` 和
  ``@staticmethod``。
* 搭配 ``super()`` 的继承、MRO，以及协作式多重继承。
* 让对象表现得像内置类型的 dunder（「魔法」）方法。

为什么重要
----------
当数据和操作数据的方法需要一起变化、而且你需要许多同形状的实例时，class 才
划算。要记住的查找规则：读 ``obj.attr`` 先查实例，再查类，最后查基类；
写 ``obj.attr = x`` 总是创建/更新*实例*属性，永远不会碰类。
"""

import math
from collections.abc import Iterator


class Device:
    """类属性是共享的；实例属性是每个对象自己的。"""

    category: str = "hardware"  # 不可变的类属性：读它是安全的
    tags: list[str] = []  # 坑：可变的类属性是共享的！

    def __init__(self, name: str) -> None:
        self.name = name  # 实例属性，每个对象创建时生成

    def add_tag(self, tag: str) -> None:
        # 这里改的是类级别的那个 list，所以每个实例都会看到这个 tag。
        self.tags.append(tag)


class Temperature:
    """值对象：用 property 做校验，用 dunder 做相等比较。"""

    unit: str = "C"  # 所有温度实例共享的类属性

    def __init__(self, celsius: float) -> None:
        # 通过 property 名字赋值会走 setter，于是每条构造路径（包括
        # classmethod）都会经过校验。
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        """计算/校验式访问：``temp.celsius`` 不带括号。"""
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("temperature below absolute zero")
        self._celsius = value
        # 坑：property 需要 getter 和 setter *都*有；没有 setter 时
        # ``temp.celsius = 1`` 会抛 AttributeError，这正是做只读属性的常规手法。

    @property
    def fahrenheit(self) -> float:
        """派生值：读取时计算，从不存储（因此没有同步 bug）。"""
        return Temperature.c_to_f(self.celsius)

    @classmethod
    def from_fahrenheit(cls, fahrenheit: float) -> "Temperature":
        """备用构造器。``cls`` 会尊重子类；self 做不到这点。"""
        return cls((fahrenheit - 32) * 5 / 9)

    @staticmethod
    def c_to_f(celsius: float) -> float:
        """既没有 ``self`` 也没有 ``cls``：只是一个放在 class 里的函数。"""
        return celsius * 9 / 5 + 32

    def __repr__(self) -> str:
        """无歧义的表示，给开发者和 REPL 输出用。"""
        return f"Temperature(celsius={self._celsius!r})"

    def __str__(self) -> str:
        """易读的表示，给用户和 f-string 用。"""
        return f"{self.celsius:.1f} {Temperature.unit}"

    def __eq__(self, other: object) -> bool:
        """值相等。没有它，``==`` 比较的是身份（内存地址）。"""
        if not isinstance(other, Temperature):
            # 不是 Temperature：把决定权交给另一个操作数。
            return NotImplemented  # type: ignore[return-value]
        return self._celsius == other._celsius

    def __hash__(self) -> int:
        # 坑：定义 __eq__ 会把 __hash__ 置为 None，让实例不可哈希（不能做
        # dict 的 key、不能进 set）。对象不可变时就重新声明它，否则就有意
        # 让它保持不可哈希。
        return hash(("Temperature", self._celsius))

    def __lt__(self, other: "Temperature") -> bool:
        """让 sorted() 和朴素的 ``<`` 比较可用。"""
        if not isinstance(other, Temperature):
            return NotImplemented  # type: ignore[return-value]
        return self._celsius < other._celsius


class Vector:
    """一个小巧的类序列 class，dunder 方法在这里最能体现价值。"""

    def __init__(self, *components: float) -> None:
        self.components: tuple[float, ...] = components

    def __repr__(self) -> str:
        return f"Vector{self.components}"

    def __len__(self) -> int:
        """让 ``len(v)`` 和真值判断可用。"""
        return len(self.components)

    def __getitem__(self, index: int) -> float:
        """让 ``v[0]``、切片和（配合 __iter__ 的）``for x in v`` 可用。"""
        return self.components[index]

    def __iter__(self) -> Iterator[float]:
        return iter(self.components)

    def __add__(self, other: "Vector") -> "Vector":
        """``v1 + v2`` 不改动任何操作数（返回一个新对象）。"""
        if not isinstance(other, Vector):
            return NotImplemented  # type: ignore[return-value]
        if len(self) != len(other):
            raise ValueError("vectors must have the same length")
        return Vector(*(a + b for a, b in zip(self, other, strict=True)))

    def __call__(self, factor: float) -> "Vector":
        """让实例可调用：写 ``v(2)`` 而不是 ``v.scale(2)``。"""
        return Vector(*(component * factor for component in self.components))

    def dot(self, other: "Vector") -> float:
        """普通方法：动词放方法里，数据放属性里。"""
        return sum(a * b for a, b in zip(self, other, strict=True))


class Shape:
    """基类：``describe`` 里是共享行为，``area`` 里是契约。"""

    def __init__(self, name: str) -> None:
        self.name = name

    def area(self) -> float:
        # 在这里抛异常是轻量级的「抽象方法」写法。如果你希望它在实例化时就
        # 被强制检查，那就用 abc 模块（ABC + @abstractmethod）。
        raise NotImplementedError(f"{type(self).__name__} must implement area()")

    def describe(self) -> str:
        # 调用 self.area() 会分派到*子类*的实现。
        return f"{self.name}: area={self.area():.2f}"


class Circle(Shape):
    def __init__(self, radius: float) -> None:
        super().__init__("circle")  # 协作式：执行基类的 __init__
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius**2


class Square(Shape):
    def __init__(self, side: float) -> None:
        super().__init__("square")
        self.side = side

    def area(self) -> float:
        return self.side * self.side


class Base:
    def handle(self) -> str:
        return "base"


class MixinA(Base):
    def handle(self) -> str:
        return "A+" + super().handle()


class MixinB(Base):
    def handle(self) -> str:
        return "B+" + super().handle()


class Combined(MixinA, MixinB):
    """MRO：Combined -> MixinA -> MixinB -> Base -> object。"""


def class_attribute_demo() -> None:
    """展示共享、遮蔽，以及可变类属性的陷阱。"""
    first, second = Device("router"), Device("switch")
    print("instance attr :", first.name, second.name)
    print("class attr    :", first.category, "==", Device.category)

    first.add_tag("edge")  # 改动的是共享的那个类级别 list
    print("tags leak     :", second.tags)  # ……从另一个实例也看得见
    # 修法：在 __init__ 里创建 list -> ``self.tags = []``。

    first.category = "custom"  # 创建的是*实例*属性（遮蔽）
    print("shadowed      :", first.category, "| class still:", Device.category)


def property_demo() -> None:
    """Property 把属性访问变成一次方法调用。"""
    boiling = Temperature(100.0)
    print("str           :", boiling)
    print("repr          :", repr(boiling))
    print("fahrenheit    :", round(boiling.fahrenheit, 1))
    print("from_fahrenheit:", Temperature.from_fahrenheit(212.0))
    print("equal         :", boiling == Temperature(100.0), "| same object?",
          boiling is Temperature(100.0))
    print("hashable      :", len({boiling, Temperature(100.0)}))
    print("sorted        :", sorted([Temperature(30), Temperature(10)]))
    try:
        Temperature(-300)
    except ValueError as exc:
        print("validation    :", type(exc).__name__, "-", exc)


def dunder_demo() -> None:
    """Dunder 方法让你的 class 接入这门语言本身。"""
    left = Vector(1.0, 2.0)
    right = Vector(3.0, 4.0)
    print("repr / len    :", left, len(left))
    print("index / loop  :", left[0], list(left))
    print("add           :", left + right)
    print("call          :", left(10))
    print("dot           :", left.dot(right))
    print("count in dict :", {"origin": Vector(0.0, 0.0)}["origin"])


def inheritance_demo() -> None:
    """继承 + MRO + 协作式 super()。"""
    shapes: list[Shape] = [Circle(1.0), Square(2.0)]
    for shape in shapes:
        print("shape         :", shape.describe())
    print("isinstance    :", isinstance(shapes[0], Shape))
    # 坑：优先用 isinstance() 而不是 type(x) is Shape；前者尊重子类，而且
    # 对 duck-typed 代码来说它是唯一安全的检查方式。

    print("MRO           :", [cls.__name__ for cls in Combined.__mro__])
    print("cooperative   :", Combined().handle())
    # 坑：直接调用 Base.handle() 而不是 super().handle() 会破坏协作式
    # 多重继承：链条会提前中断。


def main() -> None:
    """按易读的顺序跑完所有示例。"""
    print("== class vs instance attributes ==")
    class_attribute_demo()
    print("\n== properties and dunders ==")
    property_demo()
    dunder_demo()
    print("\n== inheritance ==")
    inheritance_demo()


if __name__ == "__main__":
    main()
