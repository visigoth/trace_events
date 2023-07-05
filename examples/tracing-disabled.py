import trace_events


trace_events.init_trace(disable=True)


@trace_events.profile
def foo(value):
    return value + 1


@trace_events.counter(topic='bar calls')
def bar(value):
    value = foo(value)
    return value


if __name__ == '__main__':
    @trace_events.profile
    def baz():
        value = 0
        for x in range(0, 5):
            value += bar(x + value)
        return value

    with trace_events.timeit('main', category='entry'):
        value = baz()

    print(f'logging-example.py value={value}')
