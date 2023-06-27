from os import getpid
from threading import current_thread

from .utils import fixup_name


class CompleteEvent:
    """
    Complete event, using 'ph': 'X'
    """

    def __init__(self, name, start_time: float, duration: float, category: str = None, args: dict = None):
        self.name = fixup_name(name)
        self.category = category or 'function'
        self.process_id = getpid()
        self.thread_id = current_thread().ident
        self.start_time = start_time
        self.duration = duration
        self.args = args


class Trace:
    def __init__(self):
        self.trace_events = []
        self.other_data = {}