from .profiler import Profiler
from .utils import perf_time


class EventTimer:
    def __init__(self, name, profiler: Profiler = None, category:str = None, args: dict = None, **kwargs):
        self._name = name
        self._start_time = None
        self._category = None
        self._args = dict() if not args and kwargs else args
        if kwargs:
            self._args.update(**kwargs)
        self._profiler = profiler or Profiler.global_profiler()

    def __enter__(self):
        self._start_time = perf_time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        stop_time =  perf_time()

        if exc_type is not None:
            return False

        self._profiler.add_complete_event(
            self._name,
            self._start_time,
            stop_time,
            self._category,
            self._args)

        return True
