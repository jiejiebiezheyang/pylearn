"""15 - 并发与并行：threading、multiprocessing、asyncio 与 GIL。

本文件讲什么
------------
* 线程共享内存，以及锁能防止的丢失更新竞态。
* ``queue.Queue`` 是线程之间传递工作的安全方式。
* ``multiprocessing`` 带来真正的并行，包括 Windows（和 macOS）要求的
  ``spawn`` 启动方式与主模块保护。
* ``asyncio``：单线程、大量相互重叠的等待，不需要锁。
* 一张在三种方案之间做选择的决策表。

为什么重要
----------
GIL（global interpreter lock，全局解释器锁）意味着 CPython 同一时刻只
运行*一个*线程的 Python 字节码，所以线程加速的是等待（I/O），不是计算。
实用规则：I/O 密集且只有几十个任务 -> 线程；I/O 密集且有几千个任务 ->
asyncio；CPU 密集 -> multiprocessing。

请把本文件当脚本运行，而不是 import 它：在 Windows 上，``spawn`` 需要重
新导入这些 worker 函数，所以它们必须位于 ``__main__`` 模块里。
"""

import asyncio
import multiprocessing
import os
import queue
import threading
import time

ITERATIONS = 100_000  # 加锁演示的迭代次数
RACE_ITERATIONS = 5_000  # 竞态演示的迭代次数（每次迭代都让出 GIL）


def _increment(counter: list[int], times: int) -> None:
    """没有锁的读-改-写。不是原子操作，所以会丢更新。"""
    for _ in range(times):
        value = counter[0]  # 读
        # 故意在「读」和「写」之间让出 GIL。真实的竞态窗口比这窄得多，但确实
        # 存在；把它放大之后才能稳定地观察到丢更新，而不是碰运气。
        time.sleep(0)
        counter[0] = value + 1  # 写


def unsafe_race_demo() -> None:
    """两个线程、一个计数器、没有锁：经典的丢失更新。"""
    counter = [0]
    threads = [
        threading.Thread(target=_increment, args=(counter, RACE_ITERATIONS))
        for _ in range(2)
    ]
    for thread in threads:
        thread.start()  # start() 立即返回；线程并行运行
    for thread in threads:
        thread.join()  # 等两个都结束再读结果
    expected = RACE_ITERATIONS * 2
    print("expected    :", expected)
    print("actual      :", counter[0], "| lost:", expected - counter[0])
    # 丢失的数量每次运行都不同（运气好时会少一些）：这种非确定性正是竞态在
    # 生产环境里极难调试的原因。去掉上面那句 sleep(0) 竞态依然存在，只是窗口
    # 太窄，经常看不到 —— 这正是它危险的地方。


def locked_counter_demo() -> None:
    """同一个循环加上互斥锁：结果正确，代价是等待。"""
    counter = [0]
    lock = threading.Lock()

    def bump() -> None:
        for _ in range(ITERATIONS):
            with lock:  # 同一时刻只有一个线程能进入这个块
                counter[0] += 1

    threads = [threading.Thread(target=bump) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print("with lock   :", counter[0], "| correct:", counter[0] == ITERATIONS * 2)
    # 坑：在做慢活的时候一直持锁会把一切串行化。只保护尽可能小的临界区。
    # 坑：两把锁以不同顺序获取会死锁。确实需要多把时，永远按同一个全局
    # 顺序获取。


def queue_demo() -> None:
    """队列在线程之间搬数据，而不需要共享可变对象。"""
    work: queue.Queue[int | None] = queue.Queue()
    collected: list[int] = []

    def consume() -> None:
        while True:
            item = work.get()  # 阻塞直到有元素可取
            try:
                if item is None:  # 哨兵："不会再有工作了"
                    return
                collected.append(item * item)
            finally:
                work.task_done()  # 无论成功失败都要确认

    worker = threading.Thread(target=consume)
    worker.start()
    for value in [1, 2, 3]:
        work.put(value)
    work.put(None)
    worker.join()
    print("collected   :", collected)
    print("queue drained:", work.unfinished_tasks == 0)
    # 坑：队列不是那种读者数量固定的 channel；每个消费者线程都要发一个
    # 哨兵，否则某个 worker 会永远等下去。
    # 坑：线程默认非 daemon，会让进程一直活着；漏掉一次 join() 就可能让
    # 一个"看起来"已结束的脚本卡住。


def square_in_child(payload: int) -> int:
    """在另一个解释器里运行：必须定义在模块顶层。"""
    return payload * payload


def child_pid(payload: int) -> tuple[int, int]:
    """返回子进程自己的 pid，好让演示能证明真的跑了副本。"""
    return os.getpid(), payload * payload


def multiprocessing_demo() -> None:
    """真正的并行：每个核心一个解释器，不共享内存。"""
    # Windows 和 macOS 只支持 "spawn"；显式使用它可以让各平台行为一致
    # （Linux 默认是 "fork"）。
    context = multiprocessing.get_context("spawn")
    print("start method:", context.get_start_method())
    with context.Pool(processes=2) as pool:
        squares = pool.map(square_in_child, [1, 2, 3, 4])
        pids = pool.map(child_pid, [1, 2])
    print("pool map    :", squares)
    print("separate pids:", all(pid != os.getpid() for pid, _ in pids))
    # 坑：worker 的参数和结果必须可 pickle，而且子进程拿到的是副本。在
    # 子进程里改全局变量绝不会影响父进程。
    # 坑：spawn 一个新解释器的开销是几百毫秒。任务多就用 Pool；不要为
    # 一次很小的函数调用单开一个 Process。
    # 坑：没有 ``if __name__ == "__main__":`` 保护时，spawn 会在每个子进
    # 程里重新导入本文件，pool 永远跑不完。
    # 想要 future 和 timeout 而不是裸的 Pool 方法时，
    # ``concurrent.futures.ProcessPoolExecutor`` 是更友好的 API。


async def fetch(name: str, delay: float) -> str:
    """假装是 I/O。``await`` 会挂起当前任务，让别的任务继续跑。"""
    await asyncio.sleep(delay)
    return f"{name}({delay:.2f})"


async def asyncio_demo_body() -> None:
    """单线程，大量相互重叠的等待：不用锁，也没有竞态。"""
    delays = (0.05, 0.05, 0.05)
    coroutines = [fetch(f"task{index}", delay) for index, delay in enumerate(delays)]

    start = time.perf_counter()
    gathered = await asyncio.gather(*coroutines)  # 三个全部重叠执行
    concurrent = time.perf_counter() - start

    start = time.perf_counter()
    for index, delay in enumerate(delays):
        await fetch(f"serial{index}", delay)  # 一个接一个
    sequential = time.perf_counter() - start

    print("gathered    :", gathered)
    print("concurrent  :", f"{concurrent:.3f}s | sequential: {sequential:.3f}s")
    print("overlapped  :", concurrent < sequential)
    # 坑：一次阻塞调用（time.sleep、requests.get、很重的循环）会冻住*整个*
    # 事件循环。请用 asyncio.sleep、aiohttp，或对无法避免的阻塞工作使用
    # asyncio.to_thread()。
    # 坑：async 函数必须被 await；直接调用 fetch(...) 只会返回一个协程对
    # 象，什么都不执行（外加一条警告）。


def asyncio_demo() -> None:
    """``asyncio.run`` 掌管事件循环；从同步代码里只调用它一次。"""
    asyncio.run(asyncio_demo_body())


def choose_demo() -> None:
    """这张决策表让选择不再靠抛硬币。"""
    rows: tuple[tuple[str, str, str], ...] = (
        ("threading", "I/O bound, few dozen tasks", "shared memory, needs locks"),
        ("multiprocessing", "CPU bound, real parallelism", "copies, pickling, spawn cost"),
        ("asyncio", "many I/O waits, one thread", "async/await all the way down"),
    )
    print(f"{'tool':<16}{'use it when':<34}what you pay")
    for tool, when, cost in rows:
        print(f"{tool:<16}{when:<34}{cost}")
    # 先测量再选择：如果代码不是 I/O 密集，线程帮不上忙；如果工作本来就
    # 很快，这些复杂度全都不值得。并发是性能工具，不是风格选择。


def main() -> None:
    """按清晰易读的顺序跑完全部演示。"""
    print("== threads: race ==")
    unsafe_race_demo()
    print("\n== threads: lock ==")
    locked_counter_demo()
    print("\n== threads: queue ==")
    queue_demo()
    print("\n== multiprocessing ==")
    multiprocessing_demo()
    print("\n== asyncio ==")
    asyncio_demo()
    print("\n== which tool when ==")
    choose_demo()


if __name__ == "__main__":
    # Windows/macOS 上必需：spawn 启动方式会重新导入本文件，这个保护能防
    # 止子进程再跑一遍 main()。
    main()
