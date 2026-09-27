"""13 - 标准库巡礼：pathlib、os、json、datetime、collections、re。

本文件讲什么
------------
* ``pathlib.Path``：路径拼接、读取、写入、glob 匹配与元数据。
* ``os``：环境变量、工作目录，以及什么时候该用它。
* ``json``：dump/load，以及 JSON 无法表示的那些类型。
* ``datetime``：aware 与 naive 时间戳、日期运算、格式化、解析。
* ``collections``：``Counter``、``defaultdict`` 与 ``deque``。
* ``re``：覆盖绝大多数实际工作的那几个正则函数。

为什么重要
----------
"自带电池" 不是口号：这六个模块替你省下一堆第三方依赖。反复出现的坑
是编码（永远显式传 ``encoding="utf-8"``）、时区（naive datetime 默默
表示 "本地时间"）以及正则（永远写成原始字符串，这样 ``\\d`` 不会被当
成转义序列）。
"""

import json
import os
import re
import tempfile
from collections import Counter, defaultdict, deque
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# 在 import 时编译一次：re 内部也有缓存，但模块级名字能说明本文件依赖
# 哪些模式。``r"..."`` 是原始字符串，所以反斜杠原样送达正则引擎
# （ruff W605）。
DATE_RE = re.compile(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})")
EMAIL_RE = re.compile(r"\w+@\w+\.\w+")


def pathlib_demo(directory: Path) -> None:
    """Path 对象取代字符串拼接和折腾 os.path 的写法。"""
    notes = directory / "notes"  # / 运算符负责拼接路径片段
    notes.mkdir(parents=True, exist_ok=True)
    daily = notes / "day1.txt"
    daily.write_text("first line\nsecond line\n", encoding="utf-8")

    print("name/stem/suffix:", daily.name, daily.stem, daily.suffix)
    print("parent name     :", daily.parent.name)
    print("exists / is_file:", daily.exists(), daily.is_file())
    print("size in bytes   :", daily.stat().st_size)
    print("read back       :", daily.read_text(encoding="utf-8").splitlines())
    print("with_suffix     :", daily.with_suffix(".md").name)
    print("iterdir         :", sorted(item.name for item in notes.iterdir()))
    print("glob *.txt      :", sorted(item.name for item in notes.glob("*.txt")))
    # 坑：永远显式传 encoding="utf-8"。不传时 open()/read_text() 会用
    # *locale* 编码（Windows 上是 cp1252 或 cp936），于是同一个文件在不同
    # 机器上读出的内容不同——经典的 "在我这儿没问题"。
    # 坑：Path.resolve() 和 .absolute() 产生的是跟机器绑定的路径，不要
    # 把它们写进配置文件、日志或测试断言。


def os_demo() -> None:
    """``os`` 管进程级的事实，``pathlib`` 管路径。"""
    print("cwd name    :", Path(os.getcwd()).name)  # 不打印绝对路径
    print("env fallback:", os.environ.get("PYLEARN_NO_SUCH_VAR", "fallback"))
    print("PATH present:", "PATH" in os.environ)
    print("os.path.join:", os.path.join("data", "file.txt"))
    print("Path join   :", (Path("data") / "file.txt").as_posix())
    print("cpu count   :", os.cpu_count())
    print("separator   :", repr(os.sep))
    # 坑：os.path 用*本地*分隔符，拼出来的字符串不可移植。用 pathlib 构造
    # 路径，只在边界处再转换。
    # 坑：修改 os.environ 会影响子进程，还会在测试之间泄漏；更推荐把配置
    # 显式传给函数。


def json_demo(directory: Path) -> None:
    """JSON 看着像 Python 字面量，其实是门小得多的语言。"""
    payload: dict[str, object] = {
        "name": "ada",
        "tags": ["math", "code"],
        "score": 91,
    }
    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    print("one line    :", json.dumps(payload, separators=(",", ":")))
    print("round trip  :", json.loads(text) == payload)

    path = directory / "payload.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    loaded: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
    print("from file   :", sorted(loaded))

    # 坑：JSON 没有 tuple、没有 set、也没有 datetime；对象的键永远是字符
    # 串，所以 int 键经过一轮往返后会变成字符串。
    try:
        json.dumps({"at": datetime(2026, 1, 2)})
    except TypeError as exc:
        print("datetime    :", type(exc).__name__)
    print("default=str :", json.dumps({"at": datetime(2026, 1, 2)}, default=str))
    # Python 默认会写出 NaN/Infinity，尽管严格 JSON 禁止它们；别的解析器
    # （JavaScript、Go）会直接拒绝这个文件。
    print("allow_nan   :", json.dumps(float("nan")))


def datetime_demo() -> None:
    """时间戳：新代码请使用 aware datetime（带时区）。"""
    stamp = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    print("isoformat   :", stamp.isoformat())
    print("fromisoformat:", datetime.fromisoformat("2026-01-02T03:04:05+00:00") == stamp)
    print("plus 90 min :", (stamp + timedelta(minutes=90)).isoformat())
    print("strftime    :", stamp.strftime("%Y-%m-%d %H:%M %Z"))
    print("strptime    :", datetime.strptime("2026/01/02", "%Y/%m/%d").date())
    print("weekday     :", date(2026, 1, 2).strftime("%A"))
    print("aware now   :", datetime.now(timezone.utc).strftime("%H:%M:%S %Z"))

    naive = datetime(2026, 1, 2, 3, 4, 5)  # 没有 tzinfo：意思是"本地，大概"
    try:
        # 坑：naive 和 aware 混着算会抛 TypeError，这是好事——悄悄猜一个
        # 时区偏移只会把日期运算结果算错。
        _ = stamp - naive
    except TypeError as exc:
        print("mixed math  :", type(exc).__name__, "-", exc)
    # 坑：datetime.utcnow() 和 .utcfromtimestamp() 返回的是 NAIVE datetime
    # （3.12 起已废弃）。请改用 datetime.now(timezone.utc)。
    # 坑：strftime/strptime 依赖当前 locale 的星期/月份名；写进文件的格式
    # 保持 "%Y-%m-%d" 这种，对外 API 用 ISO 8601。


def collections_demo() -> None:
    """覆盖计数、分组和滑动窗口的三个容器。"""
    counts: Counter[str] = Counter("abracadabra")
    print("most_common :", counts.most_common(3))
    print("total       :", sum(counts.values()), "| distinct:", len(counts))
    counts.update("aa")
    print("after update:", counts["a"])
    # Counter 的算术只保留正计数。
    print("arithmetic  :", Counter([1, 2, 2]) + Counter([2, 3]))

    groups: defaultdict[str, list[str]] = defaultdict(list)
    for name in ["ada", "bob", "alice"]:
        groups[name[0]].append(name)  # 不用先写 "if key not in dict"
    print("defaultdict :", dict(groups))
    # 坑：defaultdict 读取时也会*插入*（groups["z"] 会建出 []），所以对
    # 缺失键来说 ``if key in groups`` 的行为变了。

    recent: deque[int] = deque(maxlen=3)
    for value in range(1, 6):
        recent.append(value)
    print("deque maxlen:", list(recent))  # 只有最后三个留了下来
    recent.rotate(1)
    print("rotated     :", list(recent))
    # 坑：deque 不是 list。索引是 O(n)，不支持切片，appendleft/popleft
    # 才是最省时间的操作（O(1)）。


def regex_demo() -> None:
    """把大部分活干完的那几个正则函数。"""
    text = "release 2026-01-02, patched 2026-02-14"
    print("search      :", DATE_RE.search(text) is not None)  # 任意位置
    print("match       :", DATE_RE.match(text) is not None)  # 只从索引 0 起
    print("findall     :", DATE_RE.findall(text))  # 此处返回元组列表

    found = DATE_RE.search(text)
    if found is not None:  # search 返回 Optional[Match[str]]
        print("groups      :", found.groups(), "| named:", found.groupdict())
        print("group(1)    :", found.group(1), "| year:", found.group("year"))

    # fullmatch 用来校验：整个字符串必须匹配该模式。
    print("valid email :", bool(EMAIL_RE.fullmatch("ada@example.com")))
    print("invalid     :", bool(EMAIL_RE.fullmatch("ada@example.com!")))

    print("sub str     :", re.sub(r"\d+", "N", "a1b22"))
    print("sub fn      :", re.sub(r"\d+", lambda hit: str(int(hit.group()) * 2), "a1b22"))
    print("split       :", re.split(r"[,;]\s*", "a, b;c"))
    print("escape      :", re.escape("a.b?"))
    for hit in re.finditer(r"\d{4}", text):
        print("  found at", hit.start(), "->", hit.group())
    # 坑："." 匹配除换行外的任意字符，而 "*" 是贪婪的；"<.*>" 会一路吞到
    # 最后一个 ">"——应该改用 "<.*?>"。
    # 坑：像 (a+)+ 这种嵌套量词会引起指数级回溯。
    # 坑：永远优先用原始字符串；普通字符串里的 "\d" 现在只是弃用警告，
    # 在别的语言里直接是错误。


def main() -> None:
    """按清晰易读的顺序跑完全部演示。"""
    print("== pathlib ==")
    with tempfile.TemporaryDirectory() as raw_directory:
        directory = Path(raw_directory)
        pathlib_demo(directory)
        print("\n== json ==")
        json_demo(directory)
    print("(temporary directory removed)")

    print("\n== os ==")
    os_demo()
    print("\n== datetime ==")
    datetime_demo()
    print("\n== collections ==")
    collections_demo()
    print("\n== re ==")
    regex_demo()


if __name__ == "__main__":
    main()
