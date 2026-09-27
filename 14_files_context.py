"""14 - 文件与 context manager：with、open 模式、__enter__/__exit__。

本文件讲什么
------------
* ``with open(...)``：为什么它不是可选项，以及各个模式的含义。
* ``encoding="utf-8"`` 与 ``newline=""``：Windows 上必须的那两个参数。
* 文本模式与二进制模式、逐行读取、``seek``/``tell``。
* 围绕真实文件使用 ``csv`` 与 ``json``。
* 自己写 context manager：类形式，以及 ``@contextmanager`` 形式。

为什么重要
----------
文件句柄会占用操作系统资源；在 Windows 上没关掉的文件甚至删不掉。
``with`` 保证即使块内抛异常也会 close，而同一套协议还被锁、socket、
数据库事务和 pytest fixture 使用。一旦你会写 ``__enter__`` 和
``__exit__``，就能把任何 "先准备……再收尾" 的成对操作塞进一条语句。
"""

import csv
import json
import locale
import tempfile
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from types import TracebackType
from typing import Literal


class LineCounter:
    """用类写成的 context manager。

    ``__enter__`` 返回被 ``as`` 绑定的对象；``__exit__`` 总会执行，并接收
    异常（成功时收到三个 None）。
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.lines = 0
        self._file = path.open("w", encoding="utf-8")  # 准备工作在这里完成

    def __enter__(self) -> "LineCounter":
        return self  # 调用方写 ``with LineCounter(p) as counter``

    def write(self, text: str) -> None:
        self._file.write(text + "\n")
        self.lines += 1

    @property
    def closed(self) -> bool:
        """让演示能证明 __exit__ 确实关掉了文件。"""
        return self._file.closed

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """收尾。返回 None（或 False）表示让异常继续向外传播。"""
        self._file.close()
        if exc_type is not None:
            print("   cleanup after", exc_type.__name__)


class Timer:
    """最小可用的 context manager：测量一段代码的耗时。"""

    def __init__(self, label: str) -> None:
        self.label = label
        self.elapsed = 0.0
        self._start = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        """返回值类型写成 ``Literal[False]``：它承诺这里*永远*不会压制异常。"""
        self.elapsed = time.perf_counter() - self._start
        # 返回 True 会*压制*异常。悄悄吞掉错误正是脏数据流进生产环境的方式，
        # 所以返回 False。类型标注 Literal[False] 让 mypy 帮你守住这条承诺。
        return False


@contextmanager
def temporary_setting(settings: dict[str, str], key: str, value: str) -> Iterator[None]:
    """由生成器写成的 context manager：``yield`` 之前的代码是 __enter__，
    之后的代码是 __exit__。把收尾放进 try/finally，这样块内抛异常时收尾
    也照样执行。"""
    previous = settings.get(key)
    settings[key] = value
    try:
        yield
    finally:
        if previous is None:
            settings.pop(key, None)
        else:
            settings[key] = previous


def open_modes_demo(directory: Path) -> None:
    """各个模式：r、w（会清空！）、a、x（文件必须不存在）、b、+。"""
    path = directory / "modes.txt"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("line 1\n")
        handle.write("line 2\n")
    with path.open("a", encoding="utf-8") as handle:  # 追加，不清空
        handle.write("line 3\n")

    with path.open("r", encoding="utf-8") as handle:
        print("read()      :", repr(handle.read()))
    with path.open("r", encoding="utf-8") as handle:
        # 迭代文件是"一次流出一行"：内存恒定，10 GB 的日志文件也能读。
        # ``readlines()`` 则会把整个列表建出来。
        print("line by line:", [line.rstrip() for line in handle])
    with path.open("r", encoding="utf-8") as handle:
        first = handle.readline().rstrip()
        offset = handle.tell()
        handle.seek(0)
        print("readline    :", first, "| offset was", offset)
        print("after seek  :", handle.readline().rstrip())

    binary = directory / "raw.bin"
    binary.write_bytes(bytes([0, 1, 2, 255]))
    with binary.open("rb") as handle:  # 二进制模式：得到 bytes，绝不是 str
        print("binary read :", handle.read())
    # 坑："w" 会立刻毁掉原有内容，哪怕你一行都不写。拿不准时用 "a" 或 "x"。
    # 坑：用二进制模式打开再手工 decode 是差一错误的常见来源——文本文件
    # 就交给 open() 去解码。


def encoding_demo(directory: Path) -> None:
    """解释本文件里每个 open() 为什么都传 encoding="utf-8"。"""
    path = directory / "encoded.txt"
    # "caf\u00e9" 是 4 个字符、5 个字节，行尾另算：Linux 写 1 个 \n（共 6 字节），
    # Windows 的 write_text() 会把 \n 翻译成 \r\n（共 7 字节）。同一段代码、同一份
    # 数据，字节数就不同了；想完全掌控就显式传 newline=""（见下面的 csv_demo）。
    # 下面打印的字符数用 strip() 去掉了行尾，所以两个平台都显示 4。
    path.write_text("caf\u00e9\n", encoding="utf-8")
    raw = path.read_bytes()
    print("bytes on disk:", len(raw), "| characters:", len(raw.decode("utf-8").strip()))
    # 把原始字节也打出来：Windows 上会看到 b'caf\xc3\xa9\r\n'，差异一目了然。
    print("raw bytes    :", raw)
    # 默认编码取决于机器，所以同样的代码读同一个文件可能得到不同结果。
    # 中文 Windows 上是 cp936；这正是本仓库所有打印内容坚持纯 ASCII 的原因。
    print("locale default:", locale.getpreferredencoding(False))
    # 坑：把 UTF-8 按 cp1252 读会得到乱码而不是报错；按 ASCII 读则抛
    # UnicodeDecodeError。两种方式以不同形式"沉默"，所以每个边界都要显式
    # 传 encoding。
    # 下面这个演示故意不打印解码结果本身：errors="replace" 用 U+FFFD 替换
    # 坏字节，而 U+FFFD 在 cp936/cp1252 里无法编码，输出被重定向时会抛
    # UnicodeEncodeError。这里只打印长度和损坏个数，保证输出仍是纯 ASCII。
    replaced = raw.decode("ascii", errors="replace")
    print("errors=replace:", len(replaced), "chars,", replaced.count("\ufffd"), "damaged")
    # backslashreplace 把坏字节写成转义文本，既不丢信息也不破坏输出编码。
    print("backslashreplace:", raw.decode("ascii", errors="backslashreplace").strip())


def csv_demo(directory: Path) -> None:
    """``csv`` 替你处理引号、内嵌逗号和换行符。"""
    path = directory / "rows.csv"
    # 文本模式下 csv 必须传 newline=""：不传的话，模块自己写出的 \r\n 在
    # Windows 上会变成 \r\r\n（满屏空行）。
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["name", "score", "note"])
        writer.writerows([["ada", 91, "likes, commas"], ["bob", 78, "plain"]])
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            print("row         :", row)
    # 坑：电子表格可能写出 utf-8-sig（带 BOM）或 latin-1。重音字符看起来
    # 不对时，先查编码再怪解析器。
    # 坑：绝不要用 str.split(",") 解析 CSV；带引号的逗号会让它崩掉。


def json_file_demo(directory: Path) -> None:
    """``json.dump``/``json.load`` 作用于文件对象，而不是字符串。"""
    path = directory / "state.json"
    state: dict[str, object] = {"version": 2, "tags": ["a", "b"]}
    with path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)
    with path.open("r", encoding="utf-8") as handle:
        loaded: dict[str, object] = json.load(handle)
    print("version     :", loaded["version"], "| tags:", loaded["tags"])
    # 坑：json.dump 把文件内容一次性写出，所以中途崩溃会留下截断的文件。
    # 对重要数据，先写临时文件，成功后再替换原文件（原子替换）。


def custom_context_manager_demo(directory: Path) -> None:
    """类形式的、异常路径、计时器，以及生成器形式。"""
    counter = LineCounter(directory / "lines.txt")
    with counter as active:
        active.write("alpha")
        active.write("beta")
    print("lines       :", counter.lines, "| closed after with:", counter.closed)

    try:
        with LineCounter(directory / "boom.txt") as failing:
            failing.write("one")
            raise RuntimeError("body failed")
    except RuntimeError as exc:
        # __exit__ 依然执行了，所以文件已关闭，没有泄漏。
        print("propagated  :", exc, "| closed:", failing.closed)

    with Timer("sleep") as timer:
        time.sleep(0.01)
    print("timer       :", timer.label, "| elapsed >= 0:", timer.elapsed >= 0)

    settings: dict[str, str] = {"mode": "prod"}
    with temporary_setting(settings, "mode", "test"):
        print("inside      :", settings["mode"])
    print("restored    :", settings["mode"])

    with temporary_setting(settings, "trace", "on"):
        print("added       :", settings.get("trace"))
    print("removed     :", "trace" in settings)
    # 坑：@contextmanager 只在 yield 那个点执行收尾，所以裸 ``yield`` 而不
    # 配 try/finally，会在块内抛异常时把资源留在打开状态。组合多个
    # context manager 另见 contextlib.ExitStack。


def main() -> None:
    """按清晰易读的顺序跑完全部演示。"""
    with tempfile.TemporaryDirectory() as raw_directory:
        directory = Path(raw_directory)
        print("== open modes ==")
        open_modes_demo(directory)
        print("\n== encoding ==")
        encoding_demo(directory)
        print("\n== csv ==")
        csv_demo(directory)
        print("\n== json file ==")
        json_file_demo(directory)
        print("\n== custom context managers ==")
        custom_context_manager_demo(directory)
    print("\n(temporary directory removed)")


if __name__ == "__main__":
    main()
