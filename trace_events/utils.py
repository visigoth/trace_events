from time import perf_counter_ns


def fixup_name(name) -> str:
    """Fixup non-string names"""
    if type(name) == bytes:
        return name.decode('utf-8')

    if hasattr(name, '__call__'):
        return name.__name__

    return str(name)


def perf_time():
    """returns the perf_counter in microseconds"""
    return perf_counter_ns() * 1e-3
