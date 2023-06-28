from json import JSONDecoder, JSONEncoder

from .events import CompleteEvent, Trace


class TraceJsonDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=TraceJsonDecoder.from_dict)

    @staticmethod
    def from_dict(data: dict):
        if Trace.trace_events_field.name in data:
            return Trace.from_dict(data)

        event_type_field = CompleteEvent.event_type_field
        if event_type_field.name in data:
            event_type = data.get(event_type_field.name)
            assert isinstance(event_type, event_type_field.data_type), f'event_type value is {type(event_type).__name__} should be a {event_type_field.data_type}'

            if event_type == 'X':
                return CompleteEvent.from_dict(data)

        return None


class TraceJsonEncoder(JSONEncoder):
    """
    Converts trace objects to json representations
    """

    def default(self, obj):
        if isinstance(obj, CompleteEvent):
            data = dict(
                name = obj.name,
                cat = obj.category,
                ph = 'X',
                pid = obj.process_id,
                tis = obj.thread_id,
                ts = obj.start_time,
                dur = obj.duration)

            if obj.args:
                data.update(args = obj.args)

            return data

        if isinstance(obj, Trace):
            return dict(
                traceEvents = obj.trace_events,
                otherData = obj.other_data)

        return obj.__dict__