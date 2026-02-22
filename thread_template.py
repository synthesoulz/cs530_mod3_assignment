"""
CS 530 Module Three: Multithreading template (Improvement Pass 2)

Adds:
- Type hints (PEP 484 style)
- Clearer docstrings documenting the worker -> main contract
- Worker try/except with structured success/error messages sent through queue.Queue
- Main counts success vs. error separately
- Deterministic collection after join(): for _ in range(3): queue.get()
"""

import threading
import queue
import time
from datetime import datetime
from typing import Any, Dict, List


Result = Dict[str, Any]


def _timestamp() -> str:
    """Return a readable millisecond timestamp."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def _put_success(result_queue: "queue.Queue[Result]", message: str) -> None:
    """Send a success Result to the main thread."""
    result_queue.put(
        {
            "status": "success",
            "thread_name": threading.current_thread().name,
            "timestamp": _timestamp(),
            "message": message,
        }
    )


def _put_error(result_queue: "queue.Queue[Result]", message: str) -> None:
    """Send an error Result to the main thread."""
    result_queue.put(
        {
            "status": "error",
            "thread_name": threading.current_thread().name,
            "timestamp": _timestamp(),
            "message": message,
        }
    )


def functionOne(result_queue: "queue.Queue[Result]") -> None:
    """
    Worker 1: performs observable work and reports exactly one result.

    Args:
        result_queue: Thread-safe queue used to send Result dicts to main.

    Returns:
        None. This function reports via result_queue.
    """
    try:
        time.sleep(0.10)
        work = sum(i * i for i in range(2000))
        _put_success(result_queue, f"Task 1 completed (work={work})")
    except Exception as e:
        _put_error(result_queue, f"Task 1 failed: {type(e).__name__}: {e}")


def functionTwo(result_queue: "queue.Queue[Result]") -> None:
    """
    Worker 2: performs observable work and reports exactly one result.

    Args:
        result_queue: Thread-safe queue used to send Result dicts to main.

    Returns:
        None. This function reports via result_queue.
    """
    try:
        time.sleep(0.15)
        work = sum(i * 3 for i in range(3000))
        _put_success(result_queue, f"Task 2 completed (work={work})")
    except Exception as e:
        _put_error(result_queue, f"Task 2 failed: {type(e).__name__}: {e}")


def functionThree(result_queue: "queue.Queue[Result]") -> None:
    """
    Worker 3: performs observable work and reports exactly one result.

    Args:
        result_queue: Thread-safe queue used to send Result dicts to main.

    Returns:
        None. This function reports via result_queue.
    """
    try:
        time.sleep(0.05)
        work = sum(i ^ 7 for i in range(2500))
        _put_success(result_queue, f"Task 3 completed (work={work})")
    except Exception as e:
        _put_error(result_queue, f"Task 3 failed: {type(e).__name__}: {e}")


def main() -> None:
    """
    Coordinator: starts 3 threads, joins them, deterministically collects 3 results, and summarizes outcomes.

    Deterministic collection rationale:
    - We start exactly 3 workers and join them.
    - Each worker is expected to put exactly one Result dict into the queue.
    - Using `for _ in range(3): queue.get()` avoids racy `queue.empty()` checks.
    """
    result_queue: "queue.Queue[Result]" = queue.Queue()

    threads: List[threading.Thread] = [
        threading.Thread(target=functionOne, args=(result_queue,), name="one-thread"),
        threading.Thread(target=functionTwo, args=(result_queue,), name="two-thread"),
        threading.Thread(target=functionThree, args=(result_queue,), name="three-thread"),
    ]

    print(f"[{_timestamp()}] [Main] Starting 3 worker threads...")
    for t in threads:
        t.start()

    for t in threads:
        t.join()
    print(f"[{_timestamp()}] [Main] All threads joined. Collecting results...")

    results: List[Result] = []
    for _ in range(3):
        results.append(result_queue.get())

    success_count = 0
    error_count = 0

    for r in results:
        status = (r.get("status") or "unknown").upper()
        if r.get("status") == "success":
            success_count += 1
        elif r.get("status") == "error":
            error_count += 1

        print(f"  [{r.get('timestamp')}] [{r.get('thread_name')}] [{status}] {r.get('message')}")

    print(f"[{_timestamp()}] [Main] Result Summary:")
    print(f"  Total results collected: {len(results)}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {error_count}")

    if len(results) == 3 and error_count == 0:
        print(f"[{_timestamp()}] [Main] ✓ SUCCESS: All 3 workers completed successfully.")
    elif len(results) == 3:
        print(f"[{_timestamp()}] [Main] ⚠ PARTIAL: All 3 workers reported, but {error_count} failed.")
    else:
        print(f"[{_timestamp()}] [Main] ✗ ERROR: Expected 3 results, got {len(results)}.")


if __name__ == "__main__":
    main()
