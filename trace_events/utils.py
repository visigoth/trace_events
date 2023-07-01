import os
import time
import typing as t


def get_environ_flag(name: str, default_value: bool | None = None, required: bool = False) -> bool | None:
    """Retrieve a environment variable as a boolean flag
    :param name: Name of the environment variable
    :param default_value: Optional default value to return when `Name` is not found
    :param required: Flag to indicate the environment variable is required; will throw error when missing
    """
    true_values = ('TRUE', 'T', '1', 'ON', 'YES', 'Y')
    false_values = ('FALSE', 'F', '0', 'OFF', 'NO', 'N')

    value: str | None = os.getenv(name, None)

    if value is None:
        if default_value is not None:
            return default_value
        if required:
            raise ValueError(
                f'Environment variable `{name}` is not set and no default was given')
        return None

    if value.upper() not in true_values + false_values:
        def valid_values(values: t.Iterable[str]) -> str:
            return ', '.join(map(lambda value: f'`{value}`', values))

        raise ValueError(
            f'Invalid value for environment variable `{name}`: `{value}`. Valid true'
            f' values are: {valid_values(true_values)}, while valid false values are:'
            f' {valid_values(false_values)}')

    return value.upper() in true_values


def fixup_name(name) -> str:
    """Fixup non-string names"""
    if type(name) == bytes:
        return name.decode('utf-8')

    if hasattr(name, '__call__'):
        return name.__name__

    return str(name)


def perf_time():
    """returns the perf_counter in microseconds"""
    return time.perf_counter_ns() * 1e-3
