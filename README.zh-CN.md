<div align="center">

# Python 核心主题 — 16 个可运行示例

十六个带编号、自包含的 Python 文件：每个文件讲一个核心主题，每个文件都能独立运行。

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Examples](https://img.shields.io/badge/examples-16%2F16%20runnable-brightgreen.svg)](#文件索引)
[![Tests](https://img.shields.io/badge/tests-passing-success.svg)](#验证)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)

[English](README.md) | **简体中文**

</div>

> 徽章是 [shields.io](https://shields.io/) 的静态标签，用来描述本仓库的预期状态。本仓库没有 CI 工作流，因此不声称任何检查是自动通过的 —— [验证](#验证) 一节记录了真实的命令与最近一次运行的结果。

## 为什么有这个仓库

大部分 Python 教程只展示代码片段。而代码片段恰恰藏起了最容易出 bug 的部分：import、编码、可变默认参数、`__main__` 守卫。

这个仓库反过来做：**16 个带编号的脚本，每个只讲一个主题，而且只用标准库就能立刻跑起来**。

- **能运行，而不是只作示意。** 每个文件结尾都是 `if __name__ == "__main__":`，并打印一段带标签的讲解，所以 `python 05_functions.py` 永远有可读输出、退出码为 0。
- **注释解释决策，而不是复述语法。** 每个代码块都回答三个问题：这个语法解决什么问题、什么时候该用它、常见的坑是什么。
- **代码里的注释与文档字符串全部使用简体中文。** 打印输出保持纯 ASCII，因此在任何控制台（包括 Windows 的 cp936、cp1252 代码页）显示效果都一致，重定向到文件时也不会抛 `UnicodeEncodeError`。
- **带类型注解。** 函数签名和关键变量都有类型提示，注释里会说明这个注解带来了什么（以及它在哪里只是文档）。
- **只用标准库。** 示例不需要任何第三方包；`pytest`、`mypy`、`ruff` 只是可选的开发工具。
- **篇幅适中。** 每个文件大约 100–250 行：长到足够真实，短到能一口气读完。

它**不是**：语言参考手册、框架，也不是完整课程。它是一副注释详尽的骨架，供你修改、弄坏、重跑。

## 环境要求

| 项目     | 版本            | 原因                                                                                                                                         |
| -------- | --------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Python   | **3.10 或更高** | `match`/`case`（04）、`X \| Y` 注解（12）、`dataclass(slots=True, kw_only=True)`（09）、`zip(strict=True)`（04）、`itertools.pairwise`（07） |
| 运行依赖 | 无              | 所有示例只导入标准库                                                                                                                         |
| 开发工具 | 可选            | `pytest`、`mypy`、`ruff` —— 仅用于下面的检查                                                                                                 |

```bash
python --version        # 期望输出 Python 3.10.x 或更高
```

示例在 Windows、macOS 和 Linux 上行为一致：不调用 shell 命令、不写死绝对路径，并且所有打印内容都是 ASCII，在任何终端里显示效果都一样。

## 快速开始

```bash
# 1. 获取文件
git clone https://github.com/jiejiebiezheyang/pylearn.git
cd pylearn

# 2. 创建隔离环境（推荐，但不是运行示例的必要条件）
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. 安装可选的开发工具
python -m pip install -r requirements.txt

# 4. 运行任意示例
python 01_variables.py
python 15_concurrency.py
```

在仓库根目录一次跑完全部示例：

```bash
# macOS / Linux
for f in 0*.py 1[0-5]*.py; do python "$f"; done

# Windows PowerShell
Get-ChildItem *.py | Where-Object { $_.Name -ne '16_testing_test.py' } | ForEach-Object { python $_.Name }
```

用 pytest 运行测试文件（直接 `python 16_testing_test.py` 也会调用 pytest 跑完整套测试）：

```bash
pytest -v 16_testing_test.py
```

## 文件索引

| #   | 文件                                                     | 主题                            | 关键知识点                                                                                                                                                                                                                             |
| --- | -------------------------------------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01  | [01_variables.py](01_variables.py)                       | 变量、常量约定与基本类型        | 动态类型本质是重新绑定；`None` 与 `is None`；`int` 是任意精度；浮点相等的陷阱；真值规则表；`Final` 常量；注解不会在运行时强制检查；PEP 8 命名                                                                                          |
| 02  | [02_strings.py](02_strings.py)                           | 字符串、格式化与 bytes          | f-string 格式说明符与 `=` 调试写法；切片刻处可用；`strip`/`split`/`join`/`casefold`；循环里用 `+` 是 O(n²)；UTF-8 与 ASCII；`encode`/`decode` 与 `errors="replace"`；为什么 `encoding=` 不能省                                         |
| 03  | [03_collections.py](03_collections.py)                   | list、tuple、dict、set 与推导式 | 可变性；别名、浅拷贝与深拷贝；元组解包与可哈希性；dict 顺序、`get`、`setdefault`、`\|` 合并；集合运算；列表/字典/集合推导式与生成器表达式                                                                                              |
| 04  | [04_control_flow.py](04_control_flow.py)                 | if、for、while、match/case      | `elif` 链与三元表达式；`range`、`enumerate`、`zip(strict=True)`；`for`/`while` 的 `else`；海象运算符；带守卫和映射模式的结构化模式匹配；不要在遍历时修改容器                                                                           |
| 05  | [05_functions.py](05_functions.py)                       | 函数与参数                      | 可变默认参数的 bug 与 `None` 哨兵；关键字参数；仅位置参数（`/`）与仅关键字参数（`*`）；`*args`/`**kwargs`；函数是一等对象；临时用 `lambda`，命名就写 `def`；`functools.partial`                                                        |
| 06  | [06_scope_closures.py](06_scope_closures.py)             | 作用域、闭包与装饰器            | LEGB 查找顺序；`global` 与 `nonlocal`；闭包保存状态；循环变量延迟绑定陷阱；带参数与不带参数的装饰器；`functools.wraps`；装饰器叠加；`lru_cache`                                                                                        |
| 07  | [07_iterators_generators.py](07_iterators_generators.py) | 迭代器与生成器                  | `iter`/`next`/`StopIteration`；手写迭代器类与生成器函数对比；惰性求值与一次性耗尽；`yield from`；`send`/`close`；`itertools`（`islice`、`chain`、`groupby`、`pairwise`、`product`、`tee`）；生成器表达式的内存优势                     |
| 08  | [08_oop.py](08_oop.py)                                   | 面向对象                        | 实例属性与类属性、共享可变类属性的陷阱；带校验的 `@property`；`@classmethod`/`@staticmethod`；继承、`super()` 与 MRO；魔法方法（`__repr__`、`__eq__`、`__hash__`、`__len__`、`__getitem__`、`__add__`、`__call__`）                    |
| 09  | [09_dataclasses.py](09_dataclasses.py)                   | 数据类与命名元组                | 自动生成的 `__init__`/`__repr__`/`__eq__`；`field(default_factory=...)`；`frozen`、`order`、`slots`、`kw_only`；用 `__post_init__` 校验与 `object.__setattr__`；`asdict`/`astuple`/`replace`；`NamedTuple` 以及何时比 dataclass 更合适 |
| 10  | [10_exceptions.py](10_exceptions.py)                     | 异常处理                        | `try`/`except`/`else`/`finally` 的执行顺序；具体异常写前面；携带数据的自定义异常层级；用 `raise … from exc` 保留因果链；裸 `except:` 为什么危险；`contextlib.suppress`；`finally` 里 `return` 的陷阱；`assert` 不能用来做校验          |
| 11  | [11_modules_packages.py](11_modules_packages.py)         | 模块、包与工具链                | 四种 import 形式；`__name__`、`__file__`、`sys.modules`、`sys.path`；按路径加载文件（`spec_from_file_location`）；包目录结构、`__init__.py`、相对导入；`python -m` 与 `python file.py` 的区别；venv、pip、`pyproject.toml`             |
| 12  | [12_type_annotations.py](12_type_annotations.py)         | 类型注解与静态检查              | 内置泛型；`str \| None`；`Literal`、`NewType`、`TypedDict`；用于结构化类型的 `Protocol`；`TypeVar` 与 `@overload`；`Any`/`cast` 逃生舱；`TYPE_CHECKING`；mypy 能发现哪些测试发现不了的问题                                             |
| 13  | [13_stdlib_tour.py](13_stdlib_tour.py)                   | 常用标准库                      | `pathlib` 拼路径、读写、glob 与文件元数据；`os` 处理环境变量与工作目录；`json` 读写及 JSON 无法表达的类型；aware 与 naive 的 `datetime`；`Counter`、`defaultdict`、`deque`；最值得记住的正则函数                                       |
| 14  | [14_files_context.py](14_files_context.py)               | 文件与上下文管理器              | `with open(...)` 与各种模式（`w` 会清空！）；`encoding="utf-8"` 与 `newline=""`；按行流式读取；`seek`/`tell`；`csv` 与 `json` 往返；类实现的上下文管理器；`@contextmanager` 配 `try`/`finally`                                         |
| 15  | [15_concurrency.py](15_concurrency.py)                   | 并发与并行                      | 一句话讲清 GIL；真实的丢失更新竞态与加锁修复；线程间用 `queue.Queue`；`multiprocessing` 的 `spawn` 上下文以及为什么需要 `__main__` 守卫；`asyncio.gather` 让等待重叠；选型对照表                                                       |
| 16  | [16_testing_test.py](16_testing_test.py)                 | 测试与调试                      | 纯 `assert` 测试；fixture 与每个测试的隔离；`@pytest.mark.parametrize`；`pytest.raises`/`approx`/`caplog`；内置 fixture `tmp_path` 与 `monkeypatch`；同一次运行里也能跑 `unittest.TestCase`；`pdb` 与 `logging` 工作流笔记             |

## 布局说明：为什么 16 个文件可以平铺，以及 `__main__` 的作用

**为什么平铺在一个目录里就行。** 这些文件是*脚本*，不是库。它们之间没有任何 import，文件名互不重复，编号让目录列表天然有序。如果用 `src/` 包结构加 `__init__.py`，只会凭空增加 import 的麻烦：你得用 `python -m examples.05_functions` 来运行，而 `05_functions` 根本不是合法的模块名。因为这里没有 `__init__.py`，也就不可能出现意外形成的包级循环导入；把任意一个文件单独复制出去，它依然能完整运行。

经验规则：**学习阶段用平铺脚本，有东西被别处 import 时再建包。** 一旦某个辅助函数被两个文件使用，就把它放进 `mypkg/helpers.py`，配上 `__init__.py` 再导入（两种布局都见 `11_modules_packages.py`）。

**`if __name__ == "__main__":` 在这里起什么作用。**

- 直接运行文件（`python 05_functions.py`）→ Python 把 `__name__` 设为 `"__main__"` → 执行 `main()` → 你看到完整讲解。
- 导入文件（`import 05_functions`，或 pytest 收集 `16_testing_test.py`）→ `__name__` 是模块名 → **不**执行 `main()` → 导入时没有任何副作用。
- `multiprocessing` 使用 `spawn` 启动方式时（`15_concurrency.py` 就是这么写的，也是 Windows 的默认方式），每个子进程都会重新导入该文件。如果没有这个守卫，每个子进程都会重跑整个示例、再派生子进程，永远结束不了 —— 这是 Windows 上最常见的 multiprocessing bug。

把各个示例都放进函数里（而不是写在模块顶层）等于上了双保险：导入保持安静，同时代码依然可测试、可阅读。

## 验证

所有检查都在仓库根目录执行。按你的平台复制对应代码块。

```bash
# macOS / Linux
python -m py_compile *.py                       # 16 个文件的语法检查
ruff check .                                    # 代码风格（配置在 pyproject.toml）
mypy .                                          # 类型检查，非严格模式（见下文）
for f in 0*.py 1[0-5]*.py; do python "$f"; done  # 逐个运行示例
pytest -v 16_testing_test.py                    # 运行测试文件
```

```powershell
# Windows PowerShell
Get-ChildItem *.py | ForEach-Object { python -m py_compile $_.Name }
ruff check .
mypy .
Get-ChildItem *.py | Where-Object { $_.Name -ne '16_testing_test.py' } | ForEach-Object { python $_.Name }
pytest -v 16_testing_test.py
```

### 结果

| # | 检查               | 命令                                     | 结果                                                                   |
| - | ------------------ | ---------------------------------------- | ---------------------------------------------------------------------- |
| 1 | 编译全部 16 个文件 | `python -m py_compile *.py`              | ✅ 通过 —— 16/16 个文件编译成功，无警告                                |
| 2 | 代码风格           | `ruff check .`                           | ✅ 通过 —— `All checks passed!`（ruff 0.16.9）                         |
| 3 | 类型检查           | `mypy .`                                 | ✅ 通过 —— `Success: no issues found in 16 source files`（mypy 2.3.1） |
| 4 | 运行全部示例       | 逐个执行 `python <文件名>`（全部 16 个） | ✅ 通过 —— 16/16 退出码 0，无 stderr，stdout 全为 ASCII                |
| 5 | 测试               | `pytest -v 16_testing_test.py`           | ✅ 通过 —— 20 passed in 0.13s                                          |

记录环境（两个）：CPython 3.14.4 / Linux（ruff 0.16.9、mypy 2.3.1、pytest 9.1.1）与 CPython 3.14.3 / Windows（pytest 9.1.1）。五项检查在两边都通过。与平台相关的输出在两次运行中依然不同 —— 进程号、`15_concurrency.py` 的丢更新数量、`14_files_context.py` 打印的换行翻译与 locale 编码（Windows 上是 `cp936`），以及耗时。结果同样取决于工具版本：较旧的 ruff 或 mypy 可能并不认识这里用到的规则与检查。

### 类型检查策略

`mypy` 运行在**默认的非严格模式**下，配置位于 `pyproject.toml` 的 `[tool.mypy]`。这是有意的取舍，不是遗漏：

- 若干示例故意演示动态写法：按路径加载的模块在声明接口之前只能标成 `Any`（`11_modules_packages.py`）；`# type: ignore[assignment]` 用来展示检查器会拒绝什么（`01_variables.py`）；`12_type_annotations.py` 则把 mypy 自己的报错信息当作教学材料打印出来。
- 严格模式（`mypy --strict`）会要求每个参数都写注解、禁止未标注的装饰器，并且会拒绝上面这些演示。它非常适合作为你自己项目的下一步：把示例放到一边，运行 `mypy --strict .`，看看它能挖出多少真实问题。
- 已经强制做到的部分：每个文件里的公开函数都有注解，并且当前配置模式下类型检查已经零报错（见上表）。

## 学习路线

第一遍按顺序阅读，后面的文件会用到前面建立的词汇。三轮学习法效果很好：

1. **先运行。** `python 06_scope_closures.py`，读输出，把每一行和产生它的代码对应起来。
2. **再弄坏。** 改一个值，先猜结果再运行。把 `06` 里的 `nonlocal`、`functools.wraps` 删掉，或者把 `15` 里的锁去掉，看看会发生什么。
3. **后扩展。** 给 `16_testing_test.py` 加一个用例，或给 `03_collections.py` 的推导式部分加一种新写法。

| 阶段       | 文件                   | 重点                               |
| ---------- | ---------------------- | ---------------------------------- |
| 基础       | 01 → 02 → 03 → 04      | 值、文本、容器、流程控制           |
| 构件       | 05 → 06 → 07 → 08      | 函数、作用域、惰性求值、对象       |
| 结构与安全 | 09 → 10 → 12           | 数据建模、错误处理、类型           |
| 实战       | 11 → 13 → 14 → 15 → 16 | 导入机制、标准库、文件、并发、测试 |

值得对照阅读的组合：`05` 与 `06`（参数 vs 闭包）、`08` 与 `09`（手写类 vs dataclass）、`10` 与 `14`（异常 vs 清理）、`15` 与 `16`（竞态 vs 本该抓住它的测试）。

## 许可证

[MIT](LICENSE) © 2026 jiejiebiezheyang
