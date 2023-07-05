import logging
import trace_events


logging.basicConfig(
    handlers=[logging.StreamHandler()],
    format="[%(levelname)s][%(name)s]  %(message)s",
    level=logging.DEBUG)


# Initialize trace_events with parameters for the global trace
trace_events.init_trace(
    trace_file_dir='traces',
    trace_file_name='logging-example.json',
    # save_at_exit = True
    # overwrite_trace_files=False,
    logger=logging.getLogger("trace_events")
)


# Decorate an entire method call
@trace_events.profile
def foo(value):
    return value + 1


# Count the number of times a method is entered or exited
@trace_events.profile
@trace_events.counter(topic='bar entry')
def bar(value):
    value = foo(value)
    return value


if __name__ == '__main__':
    # Decorate a local function and give it a custom category
    @trace_events.profile(category='main-function')
    def baz():
        value = 0
        for x in range(0, 5):
            value += bar(x + value)
        return value

    # Use a timing block for non-method scopes
    with trace_events.timeit('main', category='entry'):
        value = baz()
        value += baz()

    print(f'logging-example.py value={value}')
