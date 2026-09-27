"""04 - 控制流：if、for、while、range、enumerate、zip、match/case。

本文件讲什么
--------------------
* ``if`` / ``elif`` / ``else`` 与条件表达式（三元表达式）。
* 对任意可迭代对象使用 ``for``，以及 ``for ... else``。
* ``while``、``break``、``continue`` 和 ``while True:`` 惯用法。
* ``range``、``enumerate``、``zip``：不用下标算术也能拿循环计数器。
* 海象运算符 ``:=``，用于“边判断边赋值”。
* ``match`` / ``case`` 结构化模式匹配（Python 3.10+）。

为什么重要
--------------
控制流是决定可读性成败的地方。有三条规则能立刻见效：
迭代 *对象本身* 而不是下标；
用 ``enumerate``/``zip`` 代替下标杂耍；
绝不在迭代集合的同时修改它。
"""

from collections.abc import Iterable, Iterator


def if_demo() -> None:
    """条件可以是任意表达式；``elif`` 保证各分支互斥。"""
    score: int = 85
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    else:
        grade = "C"
    print("grade       :", grade)

    # 三元表达式：它是一个表达式而不是语句。适合给默认值。
    label: str = "pass" if score >= 60 else "fail"
    print("label       :", label)

    # 坑：链式比较在 Python 里可以直接写，不要把其他语言的
    # ``score >= 80 and score < 90`` 直译过来。
    print("in range    :", 80 <= score < 90)

    # 坑：``if x:`` 是判断真值，不是判断 None（见 01）。
    # 对 0 和 None 来说，``if x == 0`` 与 ``if not x`` 含义不同。
    value: int = 0
    print("not 0       :", not value, "| is None:", value is None)


def for_demo() -> None:
    """``for`` 遍历可迭代对象；它不是计数器，而是迭代器泵。"""
    total: int = 0
    for n in [1, 2, 3, 4]:
        total += n
    print("sum list    :", total)

    # range(stop) / range(start, stop) / range(start, stop, step)。
    # ``stop`` 是开区间，而且 range 是惰性的：它只存 3 个数，不是 1000 个。
    print("range       :", list(range(3)), list(range(2, 6)), list(range(0, 10, 3)))
    print("countdown   :", list(range(3, 0, -1)))

    # 坑：不要写 ``for i in range(len(items))``，用 enumerate。
    # 它更短，能处理任意可迭代对象（包括生成器），
    # 也不可能与数据不同步。
    fruits: list[str] = ["apple", "pear"]
    for index, fruit in enumerate(fruits, start=1):
        print(f"  {index}. {fruit}")

    # zip 在最短的输入处停止。``strict=True``（3.10+）会把长度不匹配
    # 变成 ValueError，而不是悄悄丢掉数据。
    names: list[str] = ["ada", "bob", "cyd"]
    ages: list[int] = [36, 41, 29]
    for name, age in zip(names, ages, strict=True):
        print(f"  {name} is {age}")

    # for ... else：只有循环没被 break 打断而正常结束时才执行 ``else``。
    for candidate in [4, 6, 8]:
        if candidate % 2:
            print("  odd found:", candidate)
            break
    else:
        print("  no odd number in the list")

    # 在循环里解包，是读取 dict 元素最自然的方式。
    inventory: dict[str, int] = {"bolts": 12, "nuts": 7}
    for part, quantity in inventory.items():
        print(f"  {part}: {quantity}")

    # 坑：绝不要在迭代 list 的同时增删元素。
    # 要么迭代副本，要么把结果收集到新 list 里。
    numbers: list[int] = [1, 2, 3, 4, 5]
    kept: list[int] = [n for n in numbers if n % 2]
    print("filtered    :", kept)


def while_demo() -> None:
    """``while`` 在条件成立时循环；``while True`` + break 也没问题。"""
    countdown: int = 3
    while countdown > 0:
        print("  tick", countdown)
        countdown -= 1

    # 重试循环：“一直重试到成功”的经典形态。
    attempts: int = 0
    while True:
        attempts += 1
        if attempts >= 3:  # 代替“操作成功了”这个条件
            break
    print("attempts    :", attempts)

    # 坑：条件永不改变的 ``while`` 会无限空转。
    # 把更新写进循环体，或者当迭代次数已知时
    # 改用 ``for``。

    total: int = 0
    n: int = 0
    while n < 10:
        n += 1
        if n % 2 == 0:
            continue  # 只跳过本次迭代剩下的部分
        total += n
    print("odd sum     :", total)

    # for/while ... else 在没有发生 ``break`` 时执行；搜索场景很好用。
    target: int = 5
    for candidate in range(3):
        if candidate == target:
            print("  found")
            break
    else:
        print("  not found, so this runs")


def walrus_demo() -> None:
    """``:=`` 在表达式内部赋值，避免重复计算。"""
    data: list[str] = ["1", "22", "333", "", "4444"]
    # 没有海象运算符的话，每个元素要调用两次 len()。
    long_enough: list[str] = [text for item in data if (text := item.strip()) and len(text) > 2]
    print("walrus      :", long_enough)

    # 常见模式：读一次、判断，然后在循环体里使用。
    queue: list[int] = [5, 0, 7]
    while queue and (value := queue.pop()) != 0:
        print("  popped", value)
    # 坑：不要为了炫技而串联海象赋值。一个表达式最多一个，
    # 而且只在它确实消除了重复计算时才用。


def match_demo() -> None:
    """``match`` 按 *结构* 而不是仅按值来选择分支。"""
    command: str = "go north 3"
    match command.split():
        # 序列模式：单词个数也参与匹配。
        case ["go", direction, distance]:
            print("move        :", direction, distance)
        case ["look"] | ["l"]:  # or 模式
            print("look around")
        case _:  # 通配符：匹配任何东西，所以要放在最后
            print("unknown command")

    # 值模式 + guard。裸名字是捕获（CAPTURE），永远不是比较：
    # ``case FAILURE:`` 会绑定一个新变量，而不是做比较。
    event: dict[str, object] = {"kind": "click", "x": 10, "y": 20}
    match event:
        # 坑：从 ``dict[str, object]`` 里捕获出来的 x/y 是 object，直接写
        # ``x > 5`` 会被 mypy 拦下（object 不支持 <）。先用 isinstance 收窄，
        # 类型检查器就满意了，运行时行为不变。
        case {"kind": "click", "x": x, "y": y} if isinstance(x, int) and x > 5:
            print("click       :", x, y)
        case {"kind": "click"}:
            print("click at origin")
        case {"kind": str() as kind}:  # 类模式 + 捕获
            print("other event :", kind)
        case _:
            print("not an event")

    # 类模式让对象自己决定什么才算重要。
    class Point:
        __match_args__ = ("x", "y")

        def __init__(self, x: int, y: int) -> None:
            self.x = x
            self.y = y

    point = Point(0, 0)
    match point:
        case Point(0, 0):
            print("origin      :", point.x, point.y)
        case Point(x=0, y=y):
            print("on y axis   :", y)
        case Point():
            print("somewhere")
    # 坑：mypy 无法证明 match 已穷尽所有情况，漏掉的 case 会静默穿过
    # （不像某些语言里那样是编译错误）。
    # 想要显式兜底时，保留最后的 ``case _:``。


def builtin_helpers_demo() -> None:
    """``any``、``all``、``sum``、带 key 的 ``min``/``max``、``reversed``。"""
    values: list[int] = [4, 9, 2]
    print("any >8      :", any(v > 8 for v in values))
    print("all >0      :", all(v > 0 for v in values))
    print("sum         :", sum(values), "| max:", max(values))
    print("max by key  :", max(values, key=lambda v: -v))
    print("reversed    :", list(reversed(values)))

    def first_long(rows: Iterable[str], minimum: int) -> Iterator[str]:
        return (row for row in rows if len(row) >= minimum)

    print("generator   :", list(first_long(["a", "bbb", "cc"], 2)))
    # 坑：``any``/``all`` 会短路，所以直接传生成器表达式
    # 比先构造一个 list 更省。


def main() -> None:
    """按可读的顺序运行每个 demo。"""
    print("== if / elif / else ==")
    if_demo()
    print("\n== for ==")
    for_demo()
    print("\n== while ==")
    while_demo()
    print("\n== walrus :=")
    walrus_demo()
    print("\n== match / case ==")
    match_demo()
    print("\n== builtin helpers ==")
    builtin_helpers_demo()


if __name__ == "__main__":
    main()
