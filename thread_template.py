"""
CS 530 Module Three: Multithreading template (Bug Introduction)

BUG: functionTwo forgets to queue.put() on success, so main blocks waiting for 3 results.
"""

import threading
import queue
import time
from datetime import datetime
from typing import Any, Dict, List


Result = Dict[str, Any]


def _timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def _put_success(result_queue: "queue.Queue[Result]", message: str) -> None:
    result_queue.put(
        {
            "status": "success",
            "thread_name": threading.current_thread().name,
            "timestamp": _timestamp(),
            "message": message,
        }
    )


def _put_error(result_queue: "queue.Queue[Result]", message: str) -> None:
    result_queue.put(
        {
            "status": "error",
            "thread_name": threading.current_thread().name,
            "timestamp": _timestamp(),
            "message": message,
        }
    )


def functionOne(result_queue: "queue.Queue[Result]") -> None:
    try:
        time.sleep(0.10)
        work = sum(i * i for i in range(2000))
        _put_success(result_queue, f"Task 1 completed (work={work})")
    except Exception as e:
        _put_error(result_queue, f"Task 1 failed: {type(e).__name__}: {e}")


def functionTwo(result_queue: "queue.Queue[Result]") -> None:
    try:
        time.sleep(0.15)
        work = sum(i * 3 for i in range(3000))

        # BUG: success result is created but NEVER queued.
        _ = {
            "status": "success",
            "thread_name": threading.current_thread().name,
            "timestamp": _timestamp(),
            "message": f"Task 2 completed (work={work})",
        }
        # Missing: result_queue.put(...)

    except Exception as e:
        _put_error(result_queue, f"Task 2 failed: {type(e).__name__}: {e}")


def functionThree(result_queue: "queue.Queue[Result]") -> None:
    try:
        time.sleep(0.05)
        work = sum(i ^ 7 for i in range(2500))
        _put_success(result_queue, f"Task 3 completed (work={work})")
    except Exception as e:
        _put_error(result_queue, f"Task 3 failed: {type(e).__name__}: {e}")


def main() -> None:
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
        # HANGS on the 3rd get() because only 2 results were queued.
        results.append(result_queue.get())

    success_count = sum(1 for r in results if r.get("status") == "success")
    error_count = sum(1 for r in results if r.get("status") == "error")

    for r in results:
        status = (r.get("status") or "unknown").upper()
        print(f"  [{r.get('timestamp')}] [{r.get('thread_name')}] [{status}] {r.get('message')}")

    print(f"[{_timestamp()}] [Main] Result Summary:")
    print(f"  Total results collected: {len(results)}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {error_count}")


if __name__ == "__main__":
    main()
