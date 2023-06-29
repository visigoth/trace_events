from os import getpid
from threading import current_thread
import typing as t

from .utils import fixup_name


class Field:
    def __init__(self, data_type: type, name: str, required: bool = True, default: t.Any = None):
        self.data_type = data_type
        self.name = name
        self.required = required
        self.default = default

        if self.default is not None:
            assert isinstance(
                self.default, self.data_type), f'{self.name} default_value should be {data_type.__name__}, but is {type(self.default).__name__}'


def get_fields(data_type: type, data: dict):
    """Extracts data fields for the given data_type from a dictionary"""

    assert hasattr(
        data_type, 'fields'), f'type:{data_type.__name__} requires a \'fields\' property'

    def mapper(field: Field):
        value = data.get(field.name, None)

        if value is None:
            if field.required:
                raise KeyError(
                    f'Required field \'{field.name}\' of {data_type.__name__} is missing from json data')

            if field.default is not None:
                return field.default

            return None

        if isinstance(value, field.data_type):
            return value

        return field.data_type(value)

    return map(mapper, data_type.fields)


class EventMetaData(type):
    """
    Event metadata

    Field properties denote the data type, name, and a flag indicating whether they are required
    """

    @property
    def name_field(cls) -> Field:
        return Field(str, 'name')

    @property
    def event_type_field(cls) -> Field:
        return Field(str, 'ph')

    @property
    def category_field(cls) -> Field:
        return Field(str, 'cat', False, 'function')

    @property
    def process_id_field(cls) -> Field:
        return Field(int, 'pid', False, 0)

    @property
    def thread_id_field(cls) -> Field:
        return Field(int, 'tis', False, 0)


class CompleteEventMetaData(EventMetaData):
    """
    CompleteEvent metadata
    """

    @property
    def event_type(cls) -> str:
        return 'X'

    @property
    def start_time_field(cls) -> Field:
        return Field(float, 'ts')

    @property
    def duration_field(cls) -> Field:
        return Field(float, 'dur')

    @property
    def args_field(cls) -> Field:
        return Field(dict, 'args', False)

    @property
    def fields(cls):
        return (cls.name_field, cls.event_type_field, cls.category_field, cls.process_id_field, cls.thread_id_field, cls.start_time_field, cls.duration_field, cls.args_field)


class CompleteEvent(object, metaclass=CompleteEventMetaData):
    """
    Complete event, using 'ph': 'X'
    """

    def __init__(self, name, start_time: float, duration: float, category: str = None, args: dict = None, process_id: int = None, thread_id: int = None):
        self.name = name if type(name) == str else fixup_name(name)
        self.category = category or CompleteEvent.category_field.default
        self.process_id = process_id if process_id is not None else getpid()
        self.thread_id = thread_id if thread_id is not None else current_thread().ident
        self.start_time = start_time
        self.duration = duration
        self.args = args

    @classmethod
    def from_dict(cls, data: dict):
        name, event_type, category, process_id, thread_id, start_time, duration, args = get_fields(
            CompleteEvent, data)
        assert event_type == 'X', 'CompleteEvent::event_type should equal \'X\''

        return CompleteEvent(
            name, start_time, duration, category=category, args=args, process_id=process_id, thread_id=thread_id)

    def to_json(self):
        data = dict(
            name=self.name,
            cat=self.category,
            ph=CompleteEvent.event_type,
            pid=self.process_id,
            tis=self.thread_id,
            ts=self.start_time,
            dur=self.duration)

        if self.args:
            data.update(args=self.args)

        return data


class CounterEventMetaData(EventMetaData):
    """
    CounterEvent metadata
    """

    @property
    def event_type(cls) -> str:
        return 'C'

    @property
    def timestamp_field(cls) -> Field:
        return Field(float, 'ts')

    @property
    def args_field(cls) -> Field:
        return Field(dict, 'args', True)

    @property
    def fields(cls):
        return (cls.name_field, cls.event_type_field, cls.category_field, cls.process_id_field, cls.thread_id_field, cls.timestamp_field, cls.args_field)


class CounterEvent(object, metaclass=CounterEventMetaData):
    """
    Counter event, using 'ph': 'C'
    """

    def __init__(self, name, timestamp: float, category: str = None, process_id: int = None, thread_id: int = None, args: dict = None):
        self.name = name if type(name) == str else fixup_name(name)
        self.category = category or CompleteEvent.category_field.default
        self.process_id = process_id if process_id is not None else getpid()
        self.thread_id = thread_id if thread_id is not None else current_thread().ident
        self.timestamp = timestamp
        self.args = args

    @staticmethod
    def from_dict(data: dict):
        name, event_type, category, process_id, thread_id, timestamp, args = get_fields(
            CounterEvent, data)
        assert event_type == 'C', 'CounterEvent::event_type should equal \'C\''

        return CounterEvent(
            name, timestamp, category=category, process_id=process_id, thread_id=thread_id, args=args)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CounterEvent):
            return False

        return (self.name, self.category, self.process_id, self.thread_id, self.timestamp, self.args) == (other.name, other.category, other.process_id, other.thread_id, other.timestamp, other.args)

    def to_json(self):
        data = dict(
            name=self.name,
            cat=self.category,
            ph=CounterEvent.event_type,
            pid=self.process_id,
            tis=self.thread_id,
            ts=self.timestamp)

        if self.args:
            data.update(args=self.args)

        return data


ALL_EVENT_TYPES = [CompleteEvent, CounterEvent]


class TraceMetaData(type):
    """
    Trace metadata
    """

    @property
    def trace_events_field(cls) -> Field:
        return Field(list, 'traceEvents', False, [])

    @property
    def other_data_field(cls) -> Field:
        return Field(dict, 'otherData', False, {})


class Trace(object, metaclass=TraceMetaData):
    def __init__(self, trace_events: list = None, other_data: dict = None):
        self.trace_events = trace_events or []
        self.other_data = other_data or {}

    @classmethod
    def from_dict(cls, data: dict):
        trace_events, other_data = get_fields(Trace, data)
        return Trace(trace_events=trace_events, other_data=other_data)
