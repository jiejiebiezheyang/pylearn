"""11 - 模块、包、import 机制与项目工具链。

本文件讲什么
------------
* import 语句的四种形式，以及模块自带的元数据。
* ``sys.modules``（导入缓存）与 ``sys.path``（搜索路径）。
* 加载一个不在 ``sys.path`` 上的 ``.py`` 文件：插件配方。
* 包的组织方式：``__init__.py``、子模块、相对导入。
* venv + pip + pyproject.toml 工作流，以命令清单的形式给出。

为什么重要
----------
``ModuleNotFoundError`` 和 "attempted relative import with no known parent
package" 是最常见的两个 Python 错误，而它们都跟搜索路径有关，跟你的
代码无关。三条事实能解释其中大部分：import 结果缓存在 ``sys.modules``；
``sys.path[0]`` 是脚本自己的目录（用 ``python -m`` 时则是当前目录）；
每个被导入的目录都必须有 ``__init__.py``（或者从 3.3 起作为 namespace
package，但那很少是你想要的结果）。
"""

import importlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

# 下面是一个模块的源码，本文件把它写进临时目录后再导入。它在启动时
# 只是一个字符串，因此不会在启动阶段导入任何东西。
MODULE_SOURCE = '''\
"""运行时创建出来的模块，用来演示 import 机制。"""

# 重新执行这个模块（importlib.reload）时旧的全局变量会保留，所以这个
# 计数器只在 reload 时自增，被导入缓存命中的那次不会增加它。
LOAD_COUNT = globals().get("LOAD_COUNT", 0) + 1

__all__ = ["double"]  # ``from module import *`` 会导出的名字


def double(value: int) -> int:
    """把一个整数翻倍。"""
    return value * 2
'''


def import_forms_demo() -> None:
    """import 的四种写法，以及每个模块都携带的元数据。"""
    # 1. import module            -> module.name
    # 2. import module as alias   -> alias.name
    # 3. from module import name  -> name
    # 4. from module import name as alias
    # 这里刻意不用 "import *"：它会隐藏名字到底来自哪里。
    print("__name__      :", __name__)
    print("this file     :", Path(__file__).name)
    print("json cached?  :", "json" in sys.modules)
    print("sys.path[0]   :", Path(sys.path[0]).name or ".")
    print("stdlib names  :", sorted(name for name in sys.modules)[:6], "...")

    # 坑：``sys.path[0]`` 的含义随启动方式而变。
    #   python 11_modules_packages.py  -> 脚本所在目录
    #   python -m 11_modules_packages  -> 当前目录
    # 这就是为什么脚本能导入身边的文件，而包里的模块一旦被直接运行就会
    # 失败。

    # 每次 import 都会执行模块的顶层代码一次，然后把得到的模块对象缓存
    # 到 sys.modules。之后重复导入几乎不花代价。
    print("same object   :", importlib.import_module("json") is json)


def dynamic_import_demo() -> None:
    """按路径导入文件——插件系统和 CLI 加载模块的方式。"""
    with tempfile.TemporaryDirectory() as raw_directory:
        directory = Path(raw_directory)
        module_path = directory / "greeter.py"
        module_path.write_text(MODULE_SOURCE, encoding="utf-8")

        print("on sys.path?  :", str(directory) in sys.path)
        try:
            importlib.import_module("greeter")
        except ModuleNotFoundError:
            print("plain import  : ModuleNotFoundError (directory is not listed)")

        # 配方 1：spec_from_file_location + module_from_spec + exec_module。
        spec = importlib.util.spec_from_file_location("greeter_plugin", module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load {module_path.name}")
        # 动态加载的模块没有静态类型，因此类型检查器看到的是 ``Any``。
        # 对带类型的插件边界，用 Protocol（见 12_type_annotations.py）
        # 描述接口，并就在这里 cast 一次。
        module: Any = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module  # 执行之前先注册，这样递归的自我
        spec.loader.exec_module(module)  # 导入才能解析到它
        print("loaded name   :", module.__name__)
        print("__all__       :", module.__all__)
        print("double(21)    :", module.double(21))
        print("load count    :", module.LOAD_COUNT)

        # 配方 2：把目录放进 sys.path，然后按普通方式导入。先让各个
        # finder 丢掉缓存，因为文件是在解释器启动之后才创建的。
        sys.path.insert(0, str(directory))
        importlib.invalidate_caches()
        try:
            greeter: Any = importlib.import_module("greeter")
            print("after sys.path:", greeter.double(4))
            print("second name   :", greeter.__name__, "| load count:", greeter.LOAD_COUNT)
            # 坑：``importlib.reload()`` 只处理 ``sys.modules[module.__name__]``
            # 里由导入机制正常登记的模块，所以上面按路径手工装载的模块不能
            # 直接 reload（会抛 ModuleNotFoundError: spec not found）。把目录
            # 放进 sys.path、用 import_module 正常导入之后，reload 才会在同一个
            # 命名空间里重新执行源码：全局变量保留，计数器自增。
            reloaded: Any = importlib.reload(greeter)
            print("reload count  :", reloaded.LOAD_COUNT)
        finally:
            sys.path.remove(str(directory))
            # 把导入缓存恢复成原样：两个模块名都要清掉。
            sys.modules.pop("greeter", None)
            sys.modules.pop("greeter_plugin", None)
    # 坑：绝不要在库代码里写 ``sys.path.append(os.getcwd())``；那会让
    # import 依赖启动目录，还可能遮蔽 stdlib 模块。


def package_layout_demo() -> None:
    """打印一个包的组织结构以及对应的导入规则。"""
    layout = (
        "mypkg/",
        "  __init__.py         # makes the directory importable: mypkg",
        "  models.py           # mypkg.models",
        "  utils/",
        "    __init__.py       # a subpackage: mypkg.utils",
        "    text.py           # mypkg.utils.text",
    )
    rules = (
        "absolute : from mypkg.utils.text import slugify   # always works",
        "relative : from .text import slugify              # inside a package only",
        "run as   : python -m mypkg.utils.text             # sys.path[0] = cwd",
        "not this : python mypkg/utils/text.py             # relative imports fail",
        "__init__ : run on first import; keep it light (no side effects)",
    )
    print("\n".join(layout))
    print()
    print("\n".join(rules))
    # 坑：空的 __init__.py 完全没问题，也很常见。在 __init__.py 里做
    # 包级导入很容易产生循环导入，改成惰性导入。
    # 坑：不同目录下两个都叫 models.py 的文件是两个不同的模块；不存在
    # 「按目录遮蔽」这种规则。


def tooling_demo() -> None:
    """venv + pip + pyproject 工作流（给出命令，不在这里执行）。"""
    steps = (
        "python -m venv .venv                        # one virtualenv per project",
        ".venv\\Scripts\\activate                     # Windows",
        "source .venv/bin/activate                   # macOS / Linux",
        "python -m pip install -r requirements.txt   # dev tools (pytest, mypy, ruff)",
        "python -m pytest -v 16_testing_test.py      # run the test file",
    )
    facts = (
        "venv          : a private site-packages directory + interpreter symlink",
        "pip           : installs into the ACTIVE environment; check with 'pip -V'",
        "requirements  : a flat list of dependencies; easy, no metadata",
        "pyproject.toml: [project] metadata + tool config (pytest, mypy, ruff)",
        "installable   : 'pip install -e .' uses pyproject.toml, not requirements",
        "lockfile      : none here on purpose; pin versions in CI when needed",
    )
    print("\n".join(steps))
    print()
    print("\n".join(facts))
    # 坑：全局安装包会把多个项目混在一起，让「在我机器上能跑」只对这一台
    # 机器成立。始终使用 venv。
    # 坑：'python' 还是 'python3' 还是 'py -3'——用 'python -m pip' 能保证
    # pip 属于你实际在运行的那个解释器。


def main() -> None:
    """按易读的顺序跑完所有演示。"""
    print("== import forms and metadata ==")
    import_forms_demo()
    print("\n== dynamic import (plugin recipe) ==")
    dynamic_import_demo()
    print("\n== package layout ==")
    package_layout_demo()
    print("\n== venv / pip / pyproject ==")
    tooling_demo()


if __name__ == "__main__":
    main()
