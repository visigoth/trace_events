from functools import wraps
from logging import Logger
from json import dump, dumps
import typing as t

from .events import CompleteEvent, CounterEvent
from .json import TraceJsonEncoder
from .trace import Trace
from .utils import perf_time


class Topics:
    _dict: t.Dict[str, int]

    def __init__(self):
        self._dict = dict()

    def increment(self, topic: str) -> int:
        # ToDo: maybe make this atomic with a lock?
        if topic in self._dict:
            self._dict[topic] += 1
        else:
            self._dict[topic] = 1

        return self._dict[topic]


class Profiler:
    _global_profiler = None

    _trace: Trace
    _topics: Topics
    _start_time: float
    _logger: Logger

    def __init__(self, set_global: bool = True, save_at_exit: bool = False, logger: Logger = None):
        self._trace = Trace()
        self._topics = Topics()
        self._start_time = perf_time()
        self._logger = logger

        if set_global:
            if Profiler._global_profiler and self._logger:
                self._logger.warn('global profiler is already set')
            Profiler._global_profiler = self

        if save_at_exit:
            # ToDo: use at_exit handler
            raise NotImplementedError()

    @classmethod
    def global_profiler(cls):
        if not cls._global_profiler:
            cls._global_profiler = Profiler(False, False, None)

        return cls._global_profiler

    @property
    def start_time(self):
        return self._start_time

    def _add_complete_event(self, name, start_time: float, end_time: float, category: str = None, args: dict = None):
        self._trace.events.append(CompleteEvent(
            name,
            start_time - self._start_time,
            end_time - start_time,
            category,
            args))

    def _add_counter_event(self, name, topic: str, timestamp: float = None, category: str = None):
        count = self._topics.increment(topic)
        timestamp = (timestamp or perf_time()) - self._start_time
        self._trace.events.append(CounterEvent(
            name, timestamp, category=category, args={topic: count}))

    def reset(self):
        self._trace = Trace()
        self._topics = Topics()
        self._start_time = perf_time()

    def save_trace(self, file_name: str = 'trace.json'):
        with open(file_name, 'w') as file:
            dump(self._trace, file, cls=TraceJsonEncoder, indent=2)

        # Reset the trace so profiler can be reused
        self.reset()

    def dump_trace(self):
        return dumps(self._trace, cls=TraceJsonEncoder, indent=2)

    def counter(self, topic: str, category: str = None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self._add_counter_event(func, topic, category=category)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def exit_counter(self, topic: str, category: str = None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                finally:
                    self._add_counter_event(func, topic, category=category)
            return wrapper
        return decorator

    def profile(self, _func=None, *, category: str = None, event_args: dict = None, **event_kwargs):
        if event_kwargs:
            event_args = event_args or dict()
            event_args.update(event_kwargs)

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = perf_time()

                try:
                    return func(*args, **kwargs)
                finally:
                    stop_time = perf_time()
                    self._add_complete_event(
                        func, start_time, stop_time, category, event_args)
            return wrapper

        if _func is None:
            return decorator

        return decorator(_func)


def counter(topic: str, category: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            Profiler.global_profiler()._add_counter_event(func, topic, category=category)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def exit_counter(topic: str, category: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            finally:
                Profiler.global_profiler()._add_counter_event(func, topic, category=category)
        return wrapper
    return decorator


def profile(_func=None, *, category: str = None, args: dict = None, **event_kwargs):
    if event_kwargs:
        args = args or dict()
        args.update(event_kwargs)

    def decorator(func):
        @wraps(func)
        def wrapper(*call_args, **call_kwargs):
            start_time = perf_time()

            try:
                return func(*call_args, **call_kwargs)
            finally:
                stop_time = perf_time()
                Profiler.global_profiler()._add_complete_event(
                    func, start_time, stop_time, category, args)

        return wrapper

    if _func is None:
        return decorator

    return decorator(_func)
