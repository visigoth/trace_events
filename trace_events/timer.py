from .context import global_context
from .profiler import Profiler, global_profiler
from .utils import fixup_name, perf_time


class EventTimer:
    _name: str
    _category: str
    _start_time: float
    _args: dict
    _profiler: Profiler

    def __init__(self, name, profiler: Profiler = None, category: str = None, args: dict = None, **kwargs):
        self._name = fixup_name(name)
        self._category = None
        self._start_time = None
        self._args = dict() if not args and kwargs else args
        if kwargs:
            self._args.update(**kwargs)
        self._profiler = profiler or global_profiler()

    def __enter__(self):
        self._start_time = perf_time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        stop_time = perf_time()

        if exc_type is not None:
            return False

        self._profiler._add_complete_event(
            self._name,
            self._start_time,
            stop_time,
            self._category,
            self._args)

        return True


def timeit(name, profiler: Profiler | None = None, category: str | None = None, args: dict | None = None, **kwargs):
    """Time a block of code

    .. code-block:: python
        with trace_events.timeit('my-block', category='suspected-slow'):
            do_my_thing()
    """

    if not global_context().enabled:
        return None

    return EventTimer(name, profiler=profiler, category=category, args=args, **kwargs)
