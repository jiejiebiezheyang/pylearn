"""01 - 变量、常量与基础类型。

本文件讲什么
--------------------
* 动态类型：名字是对象的 *绑定*（binding），不是带类型的盒子。
* ``None`` 与 ``is None`` 身份判断。
* 基础类型：``int``、``float``、``str``、``bool``。
* ``if`` 和 ``while`` 所依赖的真值（truthiness）规则。
* 类型注解与 ``UPPER_CASE`` 常量命名约定。

为什么重要
--------------
Python 在 *运行时* 绑定类型。注解完全不改变程序行为；
它只表达意图，好让 mypy 这类工具在程序运行之前报出错误。
初学者的大多数 bug 来自搞混取值、可变性和真值判断，
所以下面把大部分篇幅留给了这三件事。
"""

import math
from typing import Final, get_type_hints

# Python 没有 ``const`` 关键字。约定是用 UPPER_CASE，
# ``Final`` 注解告诉类型检查器“重新绑定这个名字就是 bug”。
# 多个函数共享的值（上限、超时、key）适合定义成常量。
MAX_RETRIES: Final[int] = 3
DEFAULT_TIMEOUT: Final[float] = 2.5
APP_NAME: Final[str] = "pyexamples"


def dynamic_typing_demo() -> None:
    """演示赋值是 *重新绑定名字*，它从不声明类型。"""
    # 注解是给类型检查器看的意图。这里用 ``object`` 最诚实，
    # 因为这个 demo 确实会把同一个名字重新绑定到别的类型上。
    value: object = 10
    print("bound to int  :", value, "->", type(value).__name__)

    value = "ten"  # 同名、新对象、新类型
    print("bound to str  :", value, "->", type(value).__name__)

    value = [1, 2, 3]
    print("bound to list :", value, "->", type(value).__name__)

    # 坑：不写 ``object`` 注解时，mypy 会从第一次赋值推断出 ``int``，
    # 从而拒绝后面的 ``str``：
    #   error: Incompatible types in assignment (expression has type "str",
    #          variable has type "int")
    # 这其实是优点：它能抓住一个名字被误用于两件事的情况。


def none_demo() -> None:
    """``None`` 是单例，意思是“暂时还没有值”。"""
    result: str | None = None

    # 坑：要用 ``is None`` 判断，不要用 ``== None``。``==`` 会调用
    # ``__eq__``，任何类都能重载它，而且 ruff/flake8 会报
    # （E711 / E714）。``is`` 比较对象身份，无法被伪造。
    print("result is None      :", result is None)
    print("type(None)          :", type(None).__name__)

    if result is None:
        result = "computed"  # 常见的“填默认值”写法
    print("after default       :", result, "| length:", len(result))

    def no_return() -> None:
        """没有 ``return`` 的函数会隐式返回 None。"""

    no_return()  # 单独调用没问题：它确实什么都没返回
    # 坑：一旦把这种调用写进表达式（比较、赋值、当参数），mypy 就报
    # func-returns-value ——「没有返回值的函数」不该被当作值使用。想验证
    # 它返回什么，读注解比读调用结果更准确。
    print("no_return() -> None :", get_type_hints(no_return)["return"] is type(None))


def numbers_demo() -> None:
    """``int`` 是任意精度整数；``float`` 是 IEEE-754 binary64。"""
    print("3 ** 40             :", 3**40)  # int 永远不会溢出
    print("7 // 2, 7 % 2       :", 7 // 2, 7 % 2)
    # 坑：整数除法向下取整（朝负无穷），不像 C 或 Java 那样
    # 向零截断。
    print("-7 // 2, -7 % 2     :", -7 // 2, -7 % 2)

    total = 0.1 + 0.2
    print("0.1 + 0.2           :", total)
    # 坑：0.1 没有精确的二进制表示，所以对浮点用 ``==`` 是陷阱。
    # 应该按容差比较（math.isclose）。
    print("0.1 + 0.2 == 0.3    :", total == 0.3)
    print("math.isclose(...)   :", math.isclose(total, 0.3))
    # 坑：金额以及任何要求精确的小数都应该放进 decimal.Decimal。
    print("round(2.675, 2)     :", round(2.675, 2))  # -> 2.67，不是 2.68


def strings_and_bools_demo() -> None:
    """``str`` 不可变；``bool`` 是 ``int`` 的子类。"""
    name = "Ada"
    # name[0] = "a"  # TypeError: 'str' does not support item assignment
    upper_name = name.upper()  # 返回新字符串，``name`` 本身不变
    print("name / upper_name   :", name, "/", upper_name)

    print("isinstance(True, int):", isinstance(True, int))
    print("True + True == 2    :", True + True == 2)
    # 坑：``and``/``or`` 返回的是某个 *操作数*，而不是 bool，
    # 所以它们可以兼作“取默认值”的惯用法。
    print("0 or 'fallback'     :", 0 or "fallback")
    print("bool([]), bool('0') :", bool([]), bool("0"))  # 注意："0" 是真值


def truthiness_demo() -> None:
    """只有这些是假值：False、None、0、0.0、''、[]、{}、set()、()。"""
    falsy_values: list[object] = [False, None, 0, 0.0, "", [], {}, set(), ()]
    for item in falsy_values:
        if not item:
            print(f"{type(item).__name__:>5} -> falsy")

    # 坑：任何非空字符串都是真值，包括 "0" 和 "False"。
    # 要用显式比较来校验，绝不能只写 ``if value:``。
    print('bool("False")       :', bool("False"))
    print('bool("0")           :', bool("0"))


def annotations_demo() -> None:
    """注解只记录类型；解释器不会强制检查它们。"""
    retries: int = 0
    timeout: float = DEFAULT_TIMEOUT
    tags: list[str] = ["core"]
    mapping: dict[str, int] = {"retries": MAX_RETRIES}
    retries += 1
    print(APP_NAME, "retries:", retries, "| max:", MAX_RETRIES)
    print("timeout:", timeout, "| tags:", tags, "| mapping:", mapping)
    # mypy 读取的是函数签名；运行时可以用 typing.get_type_hints() 拿到注解，
    # 它比直接访问 __annotations__ 更稳妥，类型检查器完全认可这个 API。
    print("type hints keys:", sorted(get_type_hints(annotations_demo)))

    # 坑：运行时没有任何东西检查注解，所以下面这行能正常运行，
    # 只有 mypy 会报错。ignore 注释用来让 ``mypy .`` 保持干净。
    wrong: int = "not an int"  # type: ignore[assignment]
    print("runtime type of 'wrong':", type(wrong).__name__)


def naming_conventions() -> None:
    """PEP 8 命名约定，这也是所有评审者和 linter 的期望。"""
    rows: tuple[tuple[str, str, str], ...] = (
        ("variables / functions", "snake_case", "retry_count, load_config"),
        ("constants", "UPPER_SNAKE_CASE", "MAX_RETRIES"),
        ("classes", "CapWords", "HttpClient"),
        ("internal helpers", "_leading_underscore", "_parse_row"),
        ("keyword clashes", "trailing_underscore", "class_, type_"),
        ("type aliases", "CapWords", "JsonValue"),
    )
    print(f"{'role':<24}{'style':<24}example")
    for role, style, example in rows:
        print(f"{role:<24}{style:<24}{example}")
    # 坑：类里两个前导下划线会触发名字改写（name mangling），
    # ``self.__x`` 会变成 ``self._ClassName__x``。表示“按约定私有”
    # 用一个下划线即可；Python 里没有真正的私有。


def main() -> None:
    """按可读的顺序运行每个 demo。"""
    print("== dynamic typing ==")
    dynamic_typing_demo()
    print("\n== None ==")
    none_demo()
    print("\n== numbers ==")
    numbers_demo()
    print("\n== str and bool ==")
    strings_and_bools_demo()
    print("\n== truthiness ==")
    truthiness_demo()
    print("\n== annotations and constants ==")
    annotations_demo()
    print("\n== naming conventions ==")
    naming_conventions()


if __name__ == "__main__":
    main()
