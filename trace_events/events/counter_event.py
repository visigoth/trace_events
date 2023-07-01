from os import getpid
from threading import current_thread

from .event import EventMetaData
from ..field import Field, get_fields


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

    name: str
    category: str
    process_id: int
    thread_id: int
    timestamp: float
    args: dict

    def __init__(self, name: str, timestamp: float, category: str = None, process_id: int = None, thread_id: int = None, args: dict = None):
        self.name = name
        self.category = category or CounterEvent.category_field.default
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

    def to_json(self) -> dict:
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
