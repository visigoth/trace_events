from os import getpid
from threading import current_thread

from .event import EventMetaData
from ..field import Field, get_fields


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
        return (
            cls.name_field,
            cls.event_type_field,
            cls.category_field,
            cls.process_id_field,
            cls.thread_id_field,
            cls.start_time_field,
            cls.duration_field,
            cls.args_field)


class CompleteEvent(object, metaclass=CompleteEventMetaData):
    """
    Complete event, using 'ph': 'X'
    """

    name: str
    category: str
    process_id: int
    thread_id: int
    start_time: float
    duration: float
    args: dict

    def __init__(self, name: str, start_time: float, duration: float, category: str = None, args: dict = None, process_id: int = None, thread_id: int = None):
        self.name = name
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

    def __eq__(self, other: object) -> bool:
        return (self.name, self.category, self.process_id, self.thread_id, self.start_time, self.duration, self.args) == (other.name, other.category, other.process_id, other.thread_id, other.start_time, other.duration, other.args)

    def to_json(self) -> dict:
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
