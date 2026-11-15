import asyncio
import time

START = time.perf_counter()


def log(msg):
    # prints elapsed seconds so you can SEE when things actually run
    print(f"[{time.perf_counter() - START:4.1f}s] {msg}")


async def brew_chai():
    log("Brewing chai...")
    await asyncio.sleep(2)
    log("Chai is ready")


async def brew(name, seconds):
    log(f"  start {name}")
    try:
        await asyncio.sleep(seconds)
    except asyncio.CancelledError:
        log(f"  CANCELLED {name}")
        raise  # always re-raise CancelledError
    log(f"  done  {name}")
    return name


async def burnt_milk():
    await asyncio.sleep(0.5)
    log("  milk burnt! raising error")
    raise ValueError("milk burnt")


# ---------------------------------------------------------------------------
# 0. Original example (unchanged behaviour)
# ---------------------------------------------------------------------------
async def demo_0_original():
    await brew_chai()


# ---------------------------------------------------------------------------
# 1. Coroutines are LAZY (unlike JS promises)
#    JS:  const p = brewChai()   -> already running
#    Py:  c = brew_chai()        -> nothing happens yet
# ---------------------------------------------------------------------------
async def demo_1_lazy():
    c = brew_chai()  # only creates a coroutine object
    log(f"created {c} - notice: no 'Brewing chai...' printed")
    await asyncio.sleep(1)
    log("1 second passed, still nothing ran")
    await c  # NOW it runs
    log("awaited it, so it ran")

    # Forgetting to await: Python warns "coroutine ... was never awaited"
    brew_chai()


# ---------------------------------------------------------------------------
# 2. create_task starts it in the background, like a JS promise
#    Small difference: JS starts the work instantly; create_task starts it
#    at your next `await` (when the event loop gets control back).
# ---------------------------------------------------------------------------
async def demo_2_create_task():
    t = asyncio.create_task(brew_chai())
    log("task created (it starts at our next await)")
    await asyncio.sleep(1)  # loop gets control -> task starts brewing
    log("doing other work while chai brews...")
    await t  # wait for it to finish
    log("task finished")


# ---------------------------------------------------------------------------
# 3. Why it matters: awaiting coroutines one by one is SEQUENTIAL
# ---------------------------------------------------------------------------
async def demo_3_sequential_vs_tasks():
    log("A) await coroutines one by one (sequential):")
    await brew("masala", 2)
    await brew("ginger", 2)  # starts only after masala finishes -> ~4s

    log("B) create tasks first, then await (concurrent):")
    t1 = asyncio.create_task(brew("masala", 2))
    t2 = asyncio.create_task(brew("ginger", 2))
    await t1
    await t2  # both ran together -> ~2s


# ---------------------------------------------------------------------------
# 4. gather does NOT cancel the others when one fails
# ---------------------------------------------------------------------------
async def demo_4_gather_failure():
    try:
        await asyncio.gather(brew("masala", 1), burnt_milk(), brew("ginger", 2))
    except ValueError as e:
        log(f"gather raised: {e!r}")

    log("waiting 2s... watch the other brews keep running in the background:")
    await asyncio.sleep(2)


# ---------------------------------------------------------------------------
# 5. TaskGroup (3.11+) DOES cancel the others when one fails
#    Like gather, but safer. Errors come wrapped in an ExceptionGroup,
#    which you catch with `except*`.
# ---------------------------------------------------------------------------
async def demo_5_taskgroup_failure():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(brew("masala", 1))
            tg.create_task(burnt_milk())
            tg.create_task(brew("ginger", 2))
    except* ValueError as eg:
        log(f"TaskGroup raised: {eg.exceptions!r}")

    log("waiting 2s... nothing else prints, the other brews were cancelled:")
    await asyncio.sleep(2)


async def main():
    global START
    for demo in [
        demo_0_original,
        demo_1_lazy,
        demo_2_create_task,
        demo_3_sequential_vs_tasks,
        demo_4_gather_failure,
        demo_5_taskgroup_failure,
    ]:
        START = time.perf_counter()  # reset the clock for each demo
        print(f"\n===== {demo.__name__} =====")
        await demo()


# asyncio.run(main=main())
main
