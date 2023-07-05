import typing as t

from .complete_event import CompleteEvent
from .counter_event import CounterEvent

AllEventTypes = [CompleteEvent, CounterEvent]

AnyEvent = t.Union[CompleteEvent, CounterEvent]

__all__ = [AllEventTypes, AnyEvent, CompleteEvent, CounterEvent]
