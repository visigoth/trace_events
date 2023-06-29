from time import sleep

from trace_events import Profiler, EventTimer, counter, profile


@profile(meta=1)
def foo(value):
    print('foo')
    sleep(0.1)
    return value + 1


@counter(topic='bar calls')
def bar(value):
    print('bar')
    with EventTimer(bar, value=value):
        sleep(0.1)
        value = foo(value)
        sleep(0.1)
    return value


if __name__ == '__main__':
    profiler = Profiler()

    @profiler.profile()
    def baz():
        value = 0
        for x in range(0, 5):
            print('baz')
            sleep(0.1)
            value += bar(1)
        return value

    with EventTimer('main', profiler):
        print('main')
        sleep(0.1)
        result = baz()
        sleep(0.1)

    profiler.save_trace(file_name='data/trace.json')
