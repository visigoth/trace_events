from json import JSONEncoder

from .events import CompleteEvent, Trace


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