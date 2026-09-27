"""03 - 复合类型：list、tuple、dict、set 与推导式。

本文件讲什么
--------------------
* ``list``：有序、可变，是“一堆东西”的默认容器。
* ``tuple``：有序、不可变、可哈希，适合固定记录。
* ``dict``：key -> value 映射，并保证插入顺序（3.7+）。
* ``set``：唯一且可哈希的值的无序集合。
* 推导式（comprehension）：用一个表达式把循环变成容器。

为什么重要
--------------
选对容器是 Python 脚本里最主要的设计工作。经验法则：
需要顺序和增删 -> list；需要固定记录 -> tuple；
需要按 key 查找 -> dict；需要去重或集合运算 -> set。

这里最常见的 bug 是 *别名*（aliasing）：两个名字指向同一个
可变对象，改一个就“改了另一个”。下面会展示各种复制辅助方法，
以及浅拷贝与深拷贝的区别。
"""

import copy
from collections.abc import Iterable


def list_demo() -> None:
    """list 可变；几乎所有 list 方法都是原地修改。"""
    numbers: list[int] = [3, 1, 2]
    numbers.append(4)  # 添加一项：[3, 1, 2, 4]
    numbers.extend([0, 5])  # 添加多项
    numbers.insert(0, 9)  # 在指定下标处插入
    print("after edits :", numbers)
    print("pop()       :", numbers.pop(), "->", numbers)  # pop 是 O(1)
    print("sorted()    :", sorted(numbers), "| original untouched:", numbers)

    # 坑：``list.sort()`` 原地排序并返回 None，而 ``sorted()``
    # 返回新 list。``x = x.sort()`` 会把 x 变成 None。
    numbers.sort()
    print("after sort() :", numbers)

    words: list[str] = ["banana", "Apple", "cherry"]
    # ``key=`` 可以避免“按大小写敏感方式比较”这个经典错误。
    print("key=casefold:", sorted(words, key=str.casefold))

    # 坑：``index`` 和 ``remove`` 是线性扫描，值不存在时抛 ValueError；
    # 如果“不存在”是正常情况，先用 ``in`` 判断。
    print("3 in numbers:", 3 in numbers)


def aliasing_demo() -> None:
    """复制容器不等于复制它的内容。"""
    original: list[int] = [1, 2, 3]
    alias = original  # 不是拷贝：同一个 list 对象有两个名字
    alias.append(4)
    print("alias shares:", original)

    safe: list[int] = original.copy()  # 浅拷贝（也可写 original[:] / list()）
    safe.append(5)
    print("copy is safe:", original, "| copy:", safe)

    # 坑：浅拷贝只复制外层容器，
    # 内层的可变对象仍然共享。
    matrix: list[list[int]] = [[1, 2], [3, 4]]
    shallow: list[list[int]] = matrix[:]
    shallow[0].append(99)
    print("shallow leak:", matrix)

    deep: list[list[int]] = copy.deepcopy(matrix)
    deep[0].append(100)
    print("deep is safe:", matrix, "| deep:", deep)
    # deepcopy 正确但不是免费的；面对大图结构，优先重建不可变数据
    # （tuple / frozen dataclass），而不是复制。


def tuple_demo() -> None:
    """tuple 不可变，所以能当 dict 的 key 和 set 的成员。"""
    point: tuple[int, int] = (3, 4)
    x, y = point  # 用解包代替 point[0], point[1]
    print("unpacked    :", x, y)
    a, b = 1, 2
    a, b = b, a  # Python 式交换，不需要临时变量
    print("swapped     :", a, b)

    first, *rest = (10, 20, 30, 40)  # 星号把“剩下的”收成一个 list
    print("star unpack :", first, rest)

    quotient, remainder = divmod(17, 5)  # 函数可以返回 tuple
    print("divmod      :", quotient, remainder)
    # 坑：让 tuple 成立的是那个逗号，而不是括号。
    print("(5) vs (5,) :", type((5)).__name__, "vs", type((5,)).__name__)

    grid: dict[tuple[int, int], str] = {(0, 0): "start", (1, 2): "goal"}
    print("tuple key   :", grid[(1, 2)])
    # 坑：只有所有元素都可哈希时 tuple 才可哈希；
    # (1, [2]) 当 dict 的 key 会抛 TypeError。不可变性也是浅的。
    print("hashable    :", hash((1, "a")) == hash((1, "a")))


def dict_demo() -> None:
    """dict 把可哈希的 key 映射到 value，并保持插入顺序。"""
    scores: dict[str, int] = {"ada": 91, "bob": 78}
    scores["cyd"] = 85  # 插入 / 覆盖
    print("scores      :", scores)

    # 坑：``scores["dee"]`` 会抛 KeyError。当“key 不存在”是正常结果时
    # 用 ``get``，需要分支判断时用 ``in``。
    print("get default :", scores.get("dee", 0), "| 'dee' in scores:", "dee" in scores)

    for name, score in scores.items():  # 同时迭代 key 和 value
        print(f"  {name:<4} -> {score}")
    print("keys/values :", list(scores), list(scores.values()))

    # ``setdefault`` 不用提前建组就能完成分组。
    groups: dict[str, list[str]] = {}
    for name in ["ada", "bob", "alice", "ben"]:
        groups.setdefault(name[0], []).append(name)
    print("grouped     :", groups)

    # Python 3.9+ 的合并运算符；``|=`` 是原地更新。
    base: dict[str, int] = {"a": 1}
    extra: dict[str, int] = {"b": 2}
    print("merged      :", base | extra, "| base untouched:", base)

    # 坑：dict 推导式和 ``to`` 风格的拷贝同样是浅拷贝。
    print("fromkeys    :", dict.fromkeys(["x", "y"], 0))
    # 坑：JSON 对象会变成 dict，但 JSON 的 key 永远是字符串；
    # json.loads 之后你原来的 int key 就没了。


def set_demo() -> None:
    """set 用来回答“这个我见过吗”，并且能快速做集合运算。"""
    seen: set[str] = set()  # {} 是空 DICT，不是空 set
    for word in ["a", "b", "a", "c"]:
        seen.add(word)
    print("unique      :", sorted(seen), "| count:", len(seen))

    left: set[int] = {1, 2, 3}
    right: set[int] = {3, 4}
    print("union       :", sorted(left | right))
    print("intersection:", sorted(left & right))
    print("difference  :", sorted(left - right))
    print("symmetric   :", sorted(left ^ right))
    print("subset      :", {3} <= left)

    # 坑：按约定 set 是无序的。对 str key 而言，迭代顺序可能因
    # 哈希随机化而在不同运行之间变化，所以只要输出或测试断言
    # 在意顺序，就始终 ``sorted()``。
    # 坑：set 成员必须可哈希：不能放 list、dict、set。
    print("dedupe fast :", len(set([1, 1, 2, 3])), "of 4 items")


def comprehension_demo() -> None:
    """推导式就是用一个表达式写“循环 + 构造容器”。"""
    squares: list[int] = [n * n for n in range(6)]
    print("squares     :", squares)

    evens: list[int] = [n for n in range(10) if n % 2 == 0]
    print("evens       :", evens)

    lengths: dict[str, int] = {word: len(word) for word in ["hi", "there"]}
    print("dict comp   :", lengths)

    unique_initials: set[str] = {name[0].upper() for name in ["ada", "alan"]}
    print("set comp    :", sorted(unique_initials))

    flat: list[int] = [n for row in [[1, 2], [3]] for n in row]  # 嵌套循环
    print("flattened   :", flat)

    # 生成器表达式是惰性的：在被消费之前什么都不算
    # （见 07_iterators_generators.py）。
    total: int = sum(n * n for n in range(5))
    print("genexpr sum :", total)

    def total_length(rows: Iterable[str]) -> int:
        return sum(len(row) for row in rows)

    print("helper sum  :", total_length(["ab", "cde"]))
    # 坑：推导式要保持简短、无副作用。如果需要两个条件再加一个 print，
    # 就写普通 ``for`` 循环，更好读也更好调试。
    # 推导式内部的变量不会泄漏到外面。


def main() -> None:
    """按可读的顺序运行每个 demo。"""
    print("== list ==")
    list_demo()
    print("\n== aliasing and copies ==")
    aliasing_demo()
    print("\n== tuple ==")
    tuple_demo()
    print("\n== dict ==")
    dict_demo()
    print("\n== set ==")
    set_demo()
    print("\n== comprehensions ==")
    comprehension_demo()


if __name__ == "__main__":
    main()
