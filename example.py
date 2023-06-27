from time import sleep

from trace_events import Profiler, EventTimer, profile


@profile(meta = 1)
def foo(value):
    print('foo')
    sleep(0.1)
    return value + 1

@profile
def bar(value):
    print('bar')
    with EventTimer(bar, value = value):
        sleep(0.1)
        value = foo(value)
        sleep(0.1)
    return value

if __name__ == '__main__':
    profiler = Profiler()

    @profiler.profile()
    def baz():
        print('baz')
        sleep(0.1)
        return bar(1)

    with EventTimer('main', profiler):
        print('main')
        sleep(0.1)
        result = baz()
        sleep(0.1)

    profiler.save_trace()