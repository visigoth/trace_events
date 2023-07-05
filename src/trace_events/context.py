from os import getcwd, path
from logging import Logger


class Context:
    """ Context manages global configuration """

    enabled: bool
    trace_file_dir: str
    global_trace_file_name: str
    overwrite_trace_files: bool
    logger: Logger | None

    def __init__(
            self, enabled: bool, trace_file_dir: str, global_trace_file_name: str,
            overwrite_trace_files: bool, logger: Logger | None):
        self.enabled = enabled or True
        self.trace_file_dir = trace_file_dir
        self.global_trace_file_name = global_trace_file_name
        self.overwrite_trace_files = overwrite_trace_files
        self.logger = logger

    def trace_file_path(self, file_name: str) -> str:
        return path.join(self.trace_file_dir, file_name)


_gloabl_context: Context = None


def init_context(
        enabled: bool = True,
        trace_file_dir: str | None = None,
        global_trace_file_name: str | None = None,
        overwrite_trace_files: bool = False,
        logger: Logger | None = None):

    file_dir = trace_file_dir or getcwd()
    file_dir = file_dir if path.isabs(file_dir) else path.abspath(file_dir)

    file_name = global_trace_file_name or 'trace.json'

    if logger:
        logger.debug(f'initializing context:')
        logger.debug(f'  enabled: {enabled}')
        logger.debug(f'  trace_file_dir: {trace_file_dir}')
        logger.debug(f'  global_trace_file_name: {file_name}')
        logger.debug(f'  overwrite_trace_files: {overwrite_trace_files}')

    global _gloabl_context
    _gloabl_context = Context(
        enabled, file_dir, file_name, overwrite_trace_files, logger)


def global_context() -> Context:
    global _gloabl_context
    if not _gloabl_context:
        init_context()
    return _gloabl_context


__all__ = [Context, init_context, global_context]
