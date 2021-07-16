import time
import functools
import threading
import collections


class RateLimiter(object):
    """[summary] Limiting API calls to Panopto server to keep it under 5 calls per second.
                 Initialise RateLimiter obj. that enforces max num
                 operations in given period (number of seconds).
    """

    def __init__(self, max_calls, period=1.0, callback=None):
        self.calls = collections.deque()
        self.period = period
        self.max_calls = max_calls
        self.callback = callback
        self._lock = threading.Lock()
        self._alock = None
        self._init_lock = threading.Lock()

    def __call__(self, f):
        """The __call__ function wraps the RateLimiter so it can be used as a
           function decorator e.g. @RateLimiter(*args)
        """

        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            with self:
                return f(*args, **kwargs)

        return wrapped

    def __enter__(self):
        """Context manager __enter__ to aquire threading lock
        Returns:
            [obj]: 
        """
        with self._lock:
            if len(self.calls) >= self.max_calls:
                until = time.time() + self.period - self._timespan
                if self.callback:
                    t = threading.Thread(target=self.callback, args=(until,))
                    t.daemon = True
                    t.start()
                sleeptime = until - time.time()
                if sleeptime > 0:
                    time.sleep(sleeptime)
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager __exit__ to release threading lock
        Returns:
            [obj]: 
        """
        with self._lock:
            self.calls.append(time.time())
            while self._timespan >= self.period:
                self.calls.popleft()

    @property
    def _timespan(self):
        return self.calls[-1] - self.calls[0]
