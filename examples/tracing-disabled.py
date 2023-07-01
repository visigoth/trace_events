from time import sleep

import trace_events


trace_events.init_trace(disable=True)


def simulate_work():
    sleep(0.01)


@trace_events.profile
def foo(value):
    sleep(0.01)
    return value + 1


@trace_events.counter(topic='bar calls')
def bar(value):
    sleep(0.01)
    value = foo(value)
    sleep(0.01)
    return value


if __name__ == '__main__':
    @trace_events.profile
    def baz():
        value = 0
        for x in range(0, 5):
            value += bar(x + value)
        return value

    with trace_events.timeit('main', category='entry'):
        baz()
