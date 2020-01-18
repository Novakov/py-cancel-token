from threading import Lock
from typing import List, Callable


class CancellationToken:
    def __init__(self):
        self._callbacks: List[Callable[[], None]] = []
        self._canceled = False
        self._completed = False
        self._lock = Lock()

    def on_cancel(self, callback: Callable[[], None]):
        if self._canceled:
            callback()
        else:
            self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[], None]):
        self._callbacks.remove(callback)

    def cancel(self):
        with self._lock:
            if self._canceled:
                return

            self._canceled = True
            self._completed = True

        for f in self._callbacks.copy():
            f()

    def complete(self):
        with self._lock:
            self._completed = True

    @property
    def cancelled(self):
        return self._canceled

    @property
    def completed(self):
        return self._completed
