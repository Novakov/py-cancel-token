from threading import Thread, Barrier
from typing import List

import pytest

from cancel_token import CancellationToken


class Counter:
    def __init__(self):
        self._count = 0

    @property
    def count(self):
        return self._count

    def inc(self):
        self._count += 1


def test_call_callback_on_cancel():
    flag = Counter()

    ct = CancellationToken()
    ct.on_cancel(flag.inc)

    ct.cancel()

    assert flag.count == 1


def test_dont_call_callback_twice():
    flag = Counter()

    ct = CancellationToken()
    ct.on_cancel(flag.inc)

    ct.cancel()
    ct.cancel()

    assert flag.count == 1


def test_call_callback_on_canceled():
    flag = Counter()

    ct = CancellationToken()
    ct.cancel()
    ct.on_cancel(flag.inc)

    assert flag.count == 1


def test_call_only_new_callback_on_canceled():
    flag = Counter()
    flag2 = Counter()

    ct = CancellationToken()
    ct.on_cancel(flag2.inc)
    ct.cancel()
    ct.on_cancel(flag.inc)

    assert flag.count == 1
    assert flag2.count == 1


def test_callback_added_from_callback():
    flag = Counter()

    ct = CancellationToken()

    def new_callback():
        flag.inc()

    def callback():
        ct.on_cancel(new_callback)

    ct.on_cancel(callback)

    ct.cancel()

    assert flag.count == 1


def test_remove_callback():
    flag = Counter()

    ct = CancellationToken()
    ct.on_cancel(flag.inc)

    ct.remove_callback(flag.inc)

    ct.cancel()

    assert flag.count == 0


def test_remove_callback_from_callback():
    flag = Counter()

    ct = CancellationToken()

    def callback2():
        flag.inc()

    def callback():
        ct.remove_callback(callback2)

    ct.on_cancel(callback)
    ct.on_cancel(callback2)

    ct.cancel()

    assert flag.count == 1


@pytest.mark.parametrize('num_threads', [5, 10])
@pytest.mark.parametrize('num_iterations', range(1, 5000, 500))
@pytest.mark.skip
def test_parallel(num_threads: int, num_iterations: int):
    flag = Counter()

    holder: List[CancellationToken] = [None]

    def setup_token():
        holder[0] = CancellationToken()
        holder[0].on_cancel(flag.inc)

    barrier = Barrier(num_threads, action=setup_token)

    def thread_proc():
        for _ in range(0, num_iterations):
            barrier.wait()
            holder[0].cancel()

    threads = [Thread(target=thread_proc) for i in range(0, num_threads)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    assert flag.count == num_iterations


def test_check_if_not_cancelled():
    ct = CancellationToken()

    assert not ct.cancelled
    assert not ct.completed


def test_check_if_cancelled():
    ct = CancellationToken()
    ct.cancel()

    assert ct.cancelled
    assert ct.completed


def test_mark_token_as_completed():
    ct = CancellationToken()

    ct.complete()

    assert not ct.cancelled
    assert ct.completed


def test_dont_call_callbacks_when_canceling_completed_token():
    ct = CancellationToken()

    flag = Counter()
    ct.on_cancel(flag.inc)

    ct.complete()

    assert flag.count == 0


def test_dont_call_callback_being_added_to_completed_token():
    ct = CancellationToken()
    flag = Counter()

    ct.complete()
    ct.on_cancel(flag.inc)

    assert flag.count == 0
