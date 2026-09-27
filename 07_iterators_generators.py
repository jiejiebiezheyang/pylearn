"""07 - Iterator 与 generator：惰性求值、yield、itertools。

本文件讲什么
------------
* Iterator protocol：``iter()``、``next()``、``StopIteration``。
* 先手写一个 iterator class，再用 generator 写同样的事。
* ``yield``、``yield from``、``send()``，以及 generator 为什么是惰性的。
* Generator expression 与 list comprehension 的对比（内存与时机）。
* 你真正会去用的那些 ``itertools`` 积木。

为什么重要
----------
惰性迭代让单个进程也能处理装不进内存的数据：日志文件、网络流、10 GB 的 CSV。
代价是 generator 只能用一次：耗尽之后就永远是空的，这是 generator 头号 bug。
``itertools`` 则提供了标准的惰性算法，让你很少需要自己写循环。
"""

import itertools
from collections.abc import Generator, Iterable, Iterator


class Countdown:
    """只要有 ``__next__`` 就是 iterator；有 ``__iter__`` 就是 iterable。

    ``__iter__`` 返回 ``self``，会让这个对象两者都是，这是「一次性 iterator」
    最常见的形态。
    """

    def __init__(self, start: int) -> None:
        self.current: int = start

    def __iter__(self) -> Iterator[int]:
        return self

    def __next__(self) -> int:
        # 抛 StopIteration 就是 iterator 表达「结束了」的方式；``for`` 和
        # ``next()`` 会把它翻译成正常的循环退出。
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1


def read_numbers(rows: Iterable[str]) -> Iterator[int]:
    """Generator function：调用它*不会*执行任何代码，只是造出一个 generator。"""
    for row in rows:
        print("   parsing", row)  # 只有真正要取元素时才会走到这里
        yield int(row)


def flatten(groups: Iterable[Iterable[int]]) -> Iterator[int]:
    """``yield from`` 直接委托给子 iterable，不用写嵌套循环。"""
    for group in groups:
        yield from group


def running_total() -> Generator[float, float, None]:
    """coroutine 风格的 generator：``yield`` 也能*接收*值。"""
    total: float = 0.0
    while True:
        received = yield total  # 发出 ``total``，同时接收 send 进来的值
        total += received


def protocol_demo() -> None:
    """手动驱动一个 iterator，看看 ``for`` 内部做了什么。"""
    values: list[int] = [10, 20]
    walker: Iterator[int] = iter(values)
    print("next        :", next(walker), next(walker))
    try:
        next(walker)
    except StopIteration:
        print("StopIteration: the iterator is done (this is not an error)")

    # 坑：iterator 走过一遍就耗尽了，所以这里打印 []。
    print("exhausted   :", list(walker))
    # list 是 *iterable* 但不是 *iterator*：iter(list) 每次都生成一个新的
    # iterator，这就是为什么 list 可以反复循环。

    print("Countdown   :", list(Countdown(4)))
    print("Countdown again (fresh object):", list(Countdown(2)))
    # 坑：上面的 class 是一次性 iterator；对同一个实例第二次调用 list() 会得到
    # []。想支持重复迭代，就让 __iter__ 返回一个新对象，而不是 self。


def generator_demo() -> None:
    """惰性：干活是按需发生的，一次一个元素。"""
    numbers = read_numbers(["1", "2", "3"])
    print("generator created; nothing parsed yet")
    print("first item  :", next(numbers))
    print("rest        :", list(numbers))  # 消费剩下的部分

    print("nested flatten:", list(flatten([[1, 2], [], [3]])))

    # Generator expression：语法和 comprehension 一样，只是用圆括号。
    squares = (n * n for n in range(6))
    print("genexpr     :", list(squares))
    # 坑：generator 没有 len()、不能索引、不能切片。只有在你确实需要随机
    # 访问、而且数据不大时，才用 list() 转换。

    # 一串 generator 组成 pipeline，让每个元素依次流过每一级。
    pipeline = (n for n in range(10) if n % 2 == 0)
    doubled = (n * 2 for n in pipeline)
    print("pipeline    :", list(doubled))

    # ``send`` 把值推回到 generator 暂停的那个 ``yield`` 处。
    totals = running_total()
    print("start       :", next(totals))  # 跑到第一个 yield
    print("send 5.0    :", totals.send(5.0))
    print("send 2.5    :", totals.send(2.5))
    totals.close()  # 长期存活的 generator 一定要 close 掉以释放资源
    # 坑：忘了先调用一次 next()/send(None)，就会得到
    # "TypeError: can't send non-None value to a just-started generator"。


def itertools_demo() -> None:
    """标准惰性算法，这样你不必自己重写一遍。"""
    # 只要有东西能让它停下来，无限 generator 就是安全的。
    print("count+islice:", list(itertools.islice(itertools.count(10, 2), 4)))
    print("cycle+islice:", list(itertools.islice(itertools.cycle("ab"), 5)))
    print("repeat      :", list(itertools.repeat("x", 3)))

    print("chain       :", list(itertools.chain([1, 2], (3,), "ab")))
    print("accumulate  :", list(itertools.accumulate([1, 2, 3, 4])))
    print("pairwise    :", list(itertools.pairwise([1, 2, 3, 4])))  # 3.10+
    print("takewhile   :", list(itertools.takewhile(lambda n: n < 3, itertools.count())))
    print("dropwhile   :", list(itertools.dropwhile(lambda n: n < 3, [1, 2, 3, 1, 4])))
    print("product     :", list(itertools.product([1, 2], "ab")))
    print("combinations:", list(itertools.combinations([1, 2, 3], 2)))
    print("permutations:", list(itertools.permutations([1, 2], 2)))

    # groupby 只把*连续*的相同 key 分到一组。要先用 key 排序，并且要在进入
    # 下一轮之前把这一组消费掉，因为 group 本身是一个 iterator，外层循环的
    # 下一步就会让它失效。
    rows: list[tuple[str, int]] = [("a", 1), ("a", 2), ("b", 3)]
    for key, group in itertools.groupby(rows, key=lambda row: row[0]):
        print("  group", key, "->", [value for _, value in group])

    # tee 把一个 iterator 拆成两个独立的 iterator（内部会做缓冲）。
    left, right = itertools.tee(iter(range(4)), 2)
    print("tee         :", list(left), list(right))


def memory_demo() -> None:
    """Generator expression 占常量内存；list 不是。"""
    expression = (n for n in range(1_000_000))
    materialised = [n for n in range(1_000_000)]
    print("genexpr type:", type(expression).__name__)
    print("list length :", len(materialised))
    del materialised  # 立刻释放；大 list 一点都不惰性
    # 坑：``sum(n for n in ...)`` 从不构造 list，而
    # ``sum([n for n in ...])`` 会构造。多出来的方括号把内存开销从 O(1)
    # 变成了 O(n) —— 通常你要的都是 generator 那种写法。
    print("first three :", list(itertools.islice(expression, 3)))


def main() -> None:
    """按易读的顺序跑完所有示例。"""
    print("== iterator protocol ==")
    protocol_demo()
    print("\n== generators ==")
    generator_demo()
    print("\n== itertools ==")
    itertools_demo()
    print("\n== memory ==")
    memory_demo()


if __name__ == "__main__":
    main()
