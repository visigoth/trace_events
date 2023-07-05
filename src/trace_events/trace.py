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
    data: dict

    def __init__(self, events: list = None, data: dict = None):
        self.events = events or []
        self.data = data or {}

    @classmethod
    def from_dict(cls, data: dict):
        """ Load from  dictionary """
        events, data = get_fields(Trace, data)
        return Trace(events=events, data=data)

    def add(self, event: AnyEvent):
        self.events.append(event)

    def add_data(self, data: dict):
        self.data.update(data)

    def to_json(self) -> dict:
        """ Convert to json """
        return dict(
            traceEvents=self.events,
            otherData=self.data)
