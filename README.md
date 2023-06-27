# Trace Events

Python event tracing using the [Trace Event Format](https://docs.google.com/document/d/1CvAClvFfyA5R-PhYUmn5OOQtYMH4h6I0nSsKchNAySU/edit)
which is supported by Chromium browsers and other tools

## Usage

Add tracing to sections of your code and execute to generate a `json` trace file

```python
import time
from trace_events import profile, Profiler, EventTimer

@profile
def foo():
    # ... do some work

@profile(category='suspected-slow')
def bar():
    time.sleep(1)

def baz(value):
    with EventTimer('baz::foo'):
        foo()

    with EventTimer('baz::bar', value=value):
        bar()


if __name__ == '__main__':
    baz(10)

    Profiler.global_profiler().save_trace('trace.json')
```

Open up a Chromium browser to [chrome://tracing](chrome://tracing) and load the file to view the trace
