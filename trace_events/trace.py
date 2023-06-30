import typing as t

from .events import AnyEvent
from .field import Field, get_fields


class TraceMetaData(type):
    """
    Trace metadata
    """

    @property
    def events_field(cls) -> Field:
        return Field(list, 'traceEvents', False, [])

    @property
    def other_data_field(cls) -> Field:
        return Field(dict, 'otherData', False, {})

    @property
    def fields(cls):
        return (cls.events_field, cls.other_data_field)


class Trace(object, metaclass=TraceMetaData):
    events: t.List[AnyEvent]
    other_data: dict

    def __init__(self, events: list = None, other_data: dict = None):
        self.events = events or []
        self.other_data = other_data or {}

    @classmethod
    def from_dict(cls, data: dict):
        events, other_data = get_fields(Trace, data)
        return Trace(events=events, other_data=other_data)

    def add(self, event: AnyEvent):
        self.events.append(event)

    def to_json(self) -> dict:
        return dict(
            traceEvents=self.events,
            otherData=self.other_data)
