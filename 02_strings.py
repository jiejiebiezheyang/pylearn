"""02 - 字符串、格式化、切片与 bytes。

本文件讲什么
--------------------
* f-string：内插表达式、格式说明符、``=`` 调试写法。
* 切片（slice）：它适用于所有序列，不只是 ``str``。
* 每天都会用到的 ``str`` 方法，以及什么时候 *不要* 用 ``+``。
* 文本与 ``bytes``：编码、解码，以及 Windows 上为什么容易踩坑。

为什么重要
--------------
文本处理占了典型脚本的大半工作量，而几乎所有“在我机器上是好的”
文本 bug 都是编码 bug。要记住的规则是：程序内部的文本是 ``str``；
一旦它跨出进程边界（磁盘、网络、子进程），它就变成 ``bytes``，
需要显式指定编码。UTF-8 在各处都是合理的默认值，
没有哪种编码能像它一样适用于所有场景。

关于输出：本文件只打印 ASCII，这样在任何控制台里显示都一样。
非 ASCII 字符在源码里写成 ``\\u`` 转义，这也证明了
源文件可以保持纯 ASCII。
"""

import textwrap

# ``\u00e9`` 是“带锐音符的 e”（UTF-8 中占 2 字节）。使用转义
# 可以让这个源文件保持 ASCII，同时仍然生成一个
# 含非 ASCII 字符的 str。
CAFE: str = "caf\u00e9"
# ``\U0001F600`` 是一个 emoji：UTF-8 中 4 字节，1 个码点，2 个 UTF-16 单元。
GRIN: str = "\U0001F600"


def fstring_demo() -> None:
    """f-string 在运行时求值花括号里的表达式。"""
    name: str = "Ada"
    score: float = 0.9234
    width: int = 42
    print(f"hello {name}, score={score:.1%}")  # .1% -> 百分比，保留 1 位小数
    print(f"width   : |{width:>8}|")  # 在 8 列内右对齐
    print(f"width   : |{width:<8}|")  # 左对齐
    print(f"width   : |{width:^8}|")  # 居中
    print(f"padded  : |{width:08d}|")  # 补零
    print(f"thousands: {1234567:,}")  # 1,234,567
    print(f"binary  : {5:04b}")  # 0101
    print(f"expr    : {2 * 3 + 1}")  # 允许任意表达式

    # Python 3.8+ 的调试写法：打印表达式、等号和取值。
    total: int = 7
    print(f"{total + 1=}")
    # 坑：Python 3.12 之前 f-string 里不能出现反斜杠，所以
    # ``f"{'\n'.join(x)}"`` 在 3.10/3.11 上是 SyntaxError。要先算好：
    joined: str = ",".join(["a", "b"])
    print(f"joined  : {joined}")
    # 坑：绝不要只靠字符串内插来构造 SQL 或 shell 命令，
    # 要用驱动/模块的参数绑定，否则有注入风险。


def slicing_demo() -> None:
    """``seq[start:stop:step]`` 复制一个区间；``stop`` 是开区间。"""
    text: str = "Python"
    print("text[0]     :", text[0])
    print("text[-1]    :", text[-1])  # 最后一项
    print("text[0:3]   :", text[0:3])  # 'Pyt'
    print("text[:3]    :", text[:3])  # start 默认为 0
    print("text[3:]    :", text[3:])  # stop 默认为末尾
    print("text[::2]   :", text[::2])  # 每隔一个字符取一个
    print("text[::-1]  :", text[::-1])  # 反转后的副本
    print("text[99:]   :", repr(text[99:]))  # 越界 slice -> 空

    # 坑：对 *list* 切片得到的是浅拷贝，所以 ``copy[:]`` 是扁平
    # list 惯用的“克隆”写法。嵌套对象仍然是共享的。
    source: list[int] = [1, 2, 3]
    shallow: list[int] = source[:]
    shallow.append(4)
    print("source      :", source, "| copy:", shallow)
    # 坑：``text[99]``（没有冒号）会抛 IndexError，切片则不会。


def methods_demo() -> None:
    """值得背下来的 str 方法。"""
    raw: str = "  Ada,Lovelace  "
    print("strip       :", repr(raw.strip()))
    parts: list[str] = raw.strip().split(",")  # split -> list[str]
    print("split       :", parts)
    print("join        :", " | ".join(parts))
    print("replace     :", "a-b-c".replace("-", "+"))
    print("startswith  :", "report.pdf".startswith(("report", "summary")))
    print("endswith    :", "report.pdf".endswith(".pdf"))
    # 坑：如果在意非 ASCII 文本，不区分大小写的比较必须用
    # casefold() 而不是 lower()（"STRASSE".casefold() == "strasse"）。
    print("casefold    :", "Stra\u00dfe".casefold() == "strasse")
    print("removeprefix:", "tmp_cache.txt".removeprefix("tmp_"))
    print("zfill       :", "7".zfill(3))
    print("count       :", "banana".count("an"))
    # 坑：``str.find`` 找不到时返回 -1；``str.index`` 会抛异常。
    print("find / index:", "banana".find("zz"), "/", "banana".index("na"))

    # 坑：循环里用 ``+`` 拼接是 O(n^2)，因为 str 不可变，
    # 每次拼接都要复制。应该先收集片段，最后 join 一次。
    chunks: list[str] = [f"row{i}" for i in range(5)]
    print("joined rows :", ";".join(chunks))

    body: str = "first line\nsecond line\nthird line"
    print("textwrap    :", textwrap.fill(body, width=18).count("\n") + 1, "lines")


def bytes_demo() -> None:
    """文本经 encode() 变成 bytes；bytes 经 decode() 变回文本。"""
    encoded: bytes = CAFE.encode("utf-8")
    print("code points        :", len(CAFE))  # 4 个字符
    print("utf-8 bytes        :", len(encoded))  # 5 字节：重音符占 2 字节
    print("utf-8 repr         :", encoded)  # ASCII 安全的转义表示
    print("round trip ok      :", encoded.decode("utf-8") == CAFE)

    # ASCII 和 latin-1 是单字节编码；UTF-8 是变长编码，
    # 所以“一个字符等于一个字节”是错的。不要按字节偏移去切文本，
    # 还指望得到合理的字符。
    print("ascii bytes of 'A' :", "A".encode("ascii"))

    # 坑：用无法表示该文本的编码去 encode 会抛 UnicodeEncodeError。
    # 处理办法是选 UTF-8（或者显式处理错误）。
    try:
        GRIN.encode("ascii")
    except UnicodeEncodeError as exc:
        print("ascii failure      :", type(exc).__name__)
    # ``errors="replace"`` 永不抛异常，但数据会被悄悄损坏；
    # 它适合日志，不适合需要往返还原的用户数据。
    print("replace fallback   :", GRIN.encode("ascii", errors="replace"))

    # 坑（Windows）：除非传了 encoding=...，否则 open() 默认用区域编码
    # （常见是 cp936 / cp1252）。读写文本文件时一定要传
    # ``encoding="utf-8"``。
    print("locale-free decode :", encoded.decode("utf-8").encode("utf-8") == encoded)


def main() -> None:
    """按可读的顺序运行每个 demo。"""
    print("== f-strings ==")
    fstring_demo()
    print("\n== slicing ==")
    slicing_demo()
    print("\n== str methods ==")
    methods_demo()
    print("\n== text vs bytes ==")
    bytes_demo()


if __name__ == "__main__":
    main()
