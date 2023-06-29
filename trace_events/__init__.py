"""
Simple event tracer using the Trace Events Format

Traces can be opened in chrome with the url: chrome://tracing
"""

__author__ = 'Jonathan Higgs'
__author_email__ = 'jonathan.higgs.11@mail.wbs.ac.uk'
__version__ = '0.1.0'


from .profiler import Profiler, counter, exit_counter, profile
from .timer import EventTimer


__all__ = [Profiler, EventTimer, counter, exit_counter, profile]
