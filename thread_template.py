"""
CS 530 Module Three: Multithreading template (Improvement Pass 1)

This version adds:
- Observable worker work (sleep + tiny compute)
- Thread-safe result collection via queue.Queue
- Deterministic result collection after join() using a fixed get() loop
- Timestamps + thread names for observability
- Verification that exactly 3 results were collected
"""

import threading
import queue
import time
from datetime import datetime


def _timestamp() -> str:
    """Return a readable millisecond timestamp."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def functionOne(result_queue: "queue.Queue[dict]") -> None:
    """Worker 1: does observable work and reports one result to the queue."""
    thread_name = threading.current_thread().name
    time.sleep(0.10)  # observable delay
    work = sum(i * i for i in range(2000))  # tiny compute
    result_queue.put(
        {
            "thread_name": thread_name,
            "timestamp": _timestamp(),
            "message": f"Task 1 completed (work={work})",
        }
    )


def functionTwo(result_queue: "queue.Queue[dict]") -> None:
    """Worker 2: does observable work and reports one result to the queue."""
    thread_name = threading.current_thread().name
    time.sleep(0.15)
    work = sum(i * 3 for i in range(3000))
    result_queue.put(
        {
            "thread_name": thread_name,
            "timestamp": _timestamp(),
            "message": f"Task 2 completed (work={work})",
        }
    )


def functionThree(result_queue: "queue.Queue[dict]") -> None:
    """Worker 3: does observable work and reports one result to the queue."""
    thread_name = threading.current_thread().name
    time.sleep(0.05)
    work = sum(i ^ 7 for i in range(2500))
    result_queue.put(
        {
            "thread_name": thread_name,
            "timestamp": _timestamp(),
            "message": f"Task 3 completed (work={work})",
        }
    )


def main() -> None:
    """
    Entry point: create, start, and join threads, then deterministically collect results.

    Deterministic collection is used (for _ in range(3): queue.get()) because:
    - After join(), we know all threads have finished.
    - We expect exactly one result per worker.
    - queue.empty() is not reliable under concurrency and can miss results or create race windows.
    """
    result_queue: "queue.Queue[dict]" = queue.Queue()

    one_thread = threading.Thread(target=functionOne, args=(result_queue,), name="one-thread")
    two_thread = threading.Thread(target=functionTwo, args=(result_queue,), name="two-thread")
    three_thread = threading.Thread(target=functionThree, args=(result_queue,), name="three-thread")

    print(f"[{_timestamp()}] [Main] Starting 3 worker threads...")
    one_thread.start()
    two_thread.start()
    three_thread.start()

    one_thread.join()
    two_thread.join()
    three_thread.join()
    print(f"[{_timestamp()}] [Main] All threads joined. Collecting results...")

    results: list[dict] = []
    # Deterministic result collection: exactly 3 gets.
    for _ in range(3):
        results.append(result_queue.get())

    for r in results:
        print(f"  [{r['timestamp']}] [{r['thread_name']}] {r['message']}")

    print(f"[{_timestamp()}] [Main] Result count: {len(results)}")
    if len(results) == 3:
        print(f"[{_timestamp()}] [Main] ✓ SUCCESS: Collected exactly 3 results.")
    else:
        print(f"[{_timestamp()}] [Main] ✗ ERROR: Expected 3 results, got {len(results)}.")


if __name__ == "__main__":
    main()
