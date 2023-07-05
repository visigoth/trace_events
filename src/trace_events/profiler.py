from datetime import datetime
from functools import wraps
from json import dump, dumps
from logging import Logger
from os import path, makedirs
import typing as t

from .context import global_context
from .events import CompleteEvent, CounterEvent
from .json import TraceJsonEncoder
from .trace import Trace
from .utils import fixup_name, perf_time


class Topics:
    """ Maintains counters """

    _counters: t.Dict[str, int]

    def __init__(self):
        self._counters = dict()

    def increment(self, topic: str):
        """ Increment the count for the given topic """
        # ToDo: maybe make this atomic with a lock?
        if topic in self._counters:
            self._counters[topic] += 1
        else:
            self._counters[topic] = 1

    def counters(self) -> dict:
        """ Return a copy of the current counters """
        return self._counters.copy()


class Profiler:
    _trace: Trace
    _topics: Topics
    _start_time: float
    _file_name: str | None
    _logger: Logger

    def __init__(self, file_name: str | None = None, logger: Logger = None):
        self._trace = Trace()
        self._topics = Topics()
        self._start_time = perf_time()
        self._file_name = file_name
        self._logger = logger

        self._trace.add_data({
            "start_time": self._start_time,
            "timestamp": datetime.now().isoformat()
        })

    @property
    def start_time(self):
        return self._start_time

    def _add_complete_event(self, name: str, start_time: float, end_time: float, category: str = None, args: dict = None):
        self._trace.events.append(CompleteEvent(
            name,
            start_time - self._start_time,
            end_time - start_time,
            category,
            args))

    def _add_counter_event(self, name: str, topic: str, timestamp: float = None, category: str = None):
        self._topics.increment(topic)
        timestamp = (timestamp or perf_time()) - self._start_time
        self._trace.events.append(CounterEvent(
            name, timestamp, category=category, args=self._topics.counters()))

    def _file_path(self, file_name: str | None) -> str:
        context = global_context()
        file_name = file_name or self._file_name or 'trace.json'
        file_path = context.trace_file_path(file_name)

        if context.overwrite_trace_files:
            return file_name

        base_name = path.splitext(path.basename(file_path))[0]
        index = 0

        while path.exists(file_path):
            file_name = f'{base_name}-{index}.json'
            file_path = context.trace_file_path(file_name)
            index += 1

        return file_path

    def reset(self):
        self._trace = Trace()
        self._topics = Topics()
        self._start_time = perf_time()

    def save_trace(self, file_name: str | None = None):
        """ Saves the trace events into the specified file """
        file_path = self._file_path(file_name)
        dir_path = path.dirname(file_path)

        if not path.exists(dir_path):
            makedirs(dir_path)

        if self._logger:
            self._logger.info(f'writing trace file to: {file_path}')

        with open(file_path, 'w') as file:
            dump(self._trace, file, cls=TraceJsonEncoder, indent=2)

    def dump_trace(self):
        return dumps(self._trace, cls=TraceJsonEncoder, indent=2, default=str)

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
                        fixup_name(func), start_time, stop_time, category, event_args)
            return wrapper

        if _func is None:
            return decorator

        return decorator(_func)


_global_profiler: Profiler = None


def _init_global_profiler():
    """ Initialize the global profiler """
    context = global_context()

    global _global_profiler
    _global_profiler = Profiler(context.global_trace_file_name)


def global_profiler() -> Profiler:
    """ Access the global profiler """
    global _global_profiler
    if not _global_profiler:
        _init_global_profiler()
    return _global_profiler


def _passthrough(func):
    """ Non-decorator to remove extra stack calls when profiler not enabled """
    return func


def add_count(name: str, topic: str, category: str = None):
    """ Manually increment the count for a topic. Traces are added to the global profiler """
    if not global_context().enabled:
        return

    profiler = global_profiler()
    if profiler is None:
        raise RuntimeWarning('Profiler is none')

    profiler._add_counter_event(fixup_name(name), topic, category=category)


def counter(topic: str, category: str = None):
    """ Adds a counter trace to the decorated function. Traces are added to the global profiler """
    if not global_context().enabled:
        return _passthrough

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global_profiler()._add_counter_event(
                fixup_name(func), topic, category=category)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def exit_counter(topic: str, category: str = None):
    """ Adds an exit counter trace to the decorated function. Traces added added to the global profiler """
    if not global_context().enabled:
        return _passthrough

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            finally:
                global_profiler()._add_counter_event(
                    fixup_name(func), topic, category=category)
        return wrapper
    return decorator


def profile(_func=None, *, category: str = None, args: dict = None, **event_kwargs):
    """ Adds method call trace to the decorated function.Traces added added to the global profiler """
    if not global_context().enabled:
        if _func is None:
            return _passthrough
        return _passthrough(_func)

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
                global_profiler()._add_complete_event(
                    fixup_name(func), start_time, stop_time, category, args)

        return wrapper

    if _func is None:
        return decorator

    return decorator(_func)
