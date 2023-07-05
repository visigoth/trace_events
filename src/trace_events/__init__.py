"""
Simple event tracer using the Trace Events Format

Traces can be opened in chrome with the url: chrome://tracing
"""

__author__ = 'Jonathan Higgs'
__author_email__ = 'jonathan.higgs.11@mail.wbs.ac.uk'
__version__ = '0.1.0'


import atexit
from logging import Logger

from .context import init_context as _init_context, global_context as _global_context
from .profiler import Profiler, global_profiler as _global_profiler, counter, exit_counter, profile
from .timer import EventTimer, timeit
from .utils import get_environ_flag as _get_environ_flag


def _save_at_exit():
    """Save the global profiler trace, registered with atexit"""

    context = _global_context()
    file_path = context.trace_file_path(context.global_trace_file_name)
    _global_profiler().save_trace(file_path)


def init_trace(
    disable: bool | None = None,
    disable_env_var: str = "TRACE_EVENTS_DISABLED",
    trace_file_dir: str | None = None,
    trace_file_name: str = "trace.json",
    save_at_exit: bool = True,
    overwrite_trace_files: bool = False,
    logger: Logger | None = None
) -> None:
    """Initializes global tracing. The `disable` controls will prevent any tracing decorators from
    inserting tracing to functions they wrap

    :param disable: Flag that will entirely disable tracing
    :param disable_env_var: Name of an environment variable to fall back on when `disable` param is not given
    :param trace_file_dir: Path to a directory prepended to file names when saving traces
    :param trace_file_name: Name of the global trace file
    :param save_at_exit: Flag to enable saving the global trace atexit, defaults to `True`
    :param overwrite_trace_files: Flag to enable overwriting existing trace files, defaults to `False`
    :param logger: Optional logger
    """

    def should_disable():
        if disable is not None:
            return disable
        if disable_env_var is not None:
            flag = _get_environ_flag(disable_env_var)
            if flag is not None:
                return flag
        return False

    enabled = not should_disable()

    _init_context(
        enabled=enabled,
        trace_file_dir=trace_file_dir,
        global_trace_file_name=trace_file_name,
        overwrite_trace_files=overwrite_trace_files,
        logger=logger)

    if not enabled:
        return

    if save_at_exit:
        atexit.register(_save_at_exit)


__all__ = [Profiler, EventTimer, init_trace,
           counter, exit_counter, profile, timeit]
