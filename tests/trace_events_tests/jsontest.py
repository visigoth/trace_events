from json import dumps, loads
from os import getpid
from threading import current_thread
import unittest

from trace_events.events import CompleteEvent, CounterEvent
from trace_events.json import TraceJsonDecoder, TraceJsonEncoder


class CompleteEventJsonTests(unittest.TestCase):

    def test_complete_event_encoding(self):
        # Arrange
        process_id = getpid()
        thread_id = current_thread().ident
        args = dict()

        event = CompleteEvent('somename', 10, 42, 'function', args=args)

        # Act
        result = dumps(event, cls=TraceJsonEncoder, indent=None)
        expected = f'{{"name": "somename", "cat": "function", "ph": "X", "pid": {process_id}, "tis": {thread_id}, "ts": 10, "dur": 42}}'

        # Assert
        self.assertEqual(result, expected)

    def test_complete_event_encoding_with_args(self):
        # Arrange
        process_id = getpid()
        thread_id = current_thread().ident
        args = dict(foo= 10)

        event = CompleteEvent('somename', 10, 42, 'function', args=args)
        expected = f'{{"name": "somename", "cat": "function", "ph": "X", "pid": {process_id}, "tis": {thread_id}, "ts": 10, "dur": 42, "args": {{"foo": 10}}}}'

        # Act
        result = dumps(event, cls=TraceJsonEncoder, indent=None)

        # Assert
        self.assertEqual(result, expected)

    def test_counter_event_decode(self):
        # Arrange
        jsonStr = '{"name": "somename", "cat": "function", "ph": "X", "pid": 5, "tis": 10, "ts": 10, "dur": 42}'

        # Act
        result = loads(jsonStr, cls=TraceJsonDecoder)

        # Assert
        self.assertIsInstance(result, CompleteEvent)
        self.assertEqual(result.name, 'somename')
        self.assertEqual(result.category, 'function')
        self.assertEqual(result.process_id, 5)
        self.assertEqual(result.thread_id, 10)
        self.assertEqual(result.start_time, 10.0)
        self.assertEqual(result.duration, 42.0)

    def test_counter_event_decode_with_defaults(self):
        # Arrange
        jsonStr = '{"name": "somename", "ph": "X", "ts": 10, "dur": 42}'

        # Act
        result = loads(jsonStr, cls=TraceJsonDecoder)

        # Assert
        self.assertIsInstance(result, CompleteEvent)
        self.assertEqual(result.name, 'somename')
        self.assertEqual(result.category, 'function')
        self.assertEqual(result.process_id, 0)
        self.assertEqual(result.thread_id, 0)
        self.assertEqual(result.start_time, 10.0)
        self.assertEqual(result.duration, 42.0)


class CounterEventJsonTests(unittest.TestCase):

    def test_counter_event_encoding(self):
        # Arrange
        process_id = getpid()
        thread_id = current_thread().ident
        args = dict()

        event = CounterEvent('somename', 10, 'function', args=args)

        # Act
        result = dumps(event, cls=TraceJsonEncoder, indent=None)
        expected = f'{{"name": "somename", "cat": "function", "ph": "C", "pid": {process_id}, "tis": {thread_id}, "ts": 10}}'

        # Assert
        self.assertEqual(result, expected)

    def test_counter_event_encoding_with_args(self):
        # Arrange
        process_id = getpid()
        thread_id = current_thread().ident
        args = dict(foo= 10)

        event = CounterEvent('somename', 10, 'function', args=args)
        expected = f'{{"name": "somename", "cat": "function", "ph": "C", "pid": {process_id}, "tis": {thread_id}, "ts": 10, "args": {{"foo": 10}}}}'

        # Act
        result = dumps(event, cls=TraceJsonEncoder, indent=None)

        # Assert
        self.assertEqual(result, expected)

    def test_counter_event_round_trip(self):
        # Arrange
        process_id = getpid()
        thread_id = current_thread().ident
        args = dict(foo= 10)

        event = CounterEvent('somename', 10, 'function', args=args, process_id=process_id, thread_id=thread_id)

        # Act
        json_string = dumps(event, cls=TraceJsonEncoder, indent=None)
        result = loads(json_string, cls=TraceJsonDecoder)

        # Assert
        self.assertEqual(result, result)
        self.assertEqual(result, event)

    def test_complete_event_decode(self):
        # Arrange
        jsonStr = '{"name": "somename", "cat": "function", "ph": "C", "pid": 5, "tis": 10, "ts": 10, "args": {"foo": 10}}'

        # Act
        result = loads(jsonStr, cls=TraceJsonDecoder)

        # Assert
        self.assertIsInstance(result, CounterEvent)
        self.assertEqual(result.name, 'somename')
        self.assertEqual(result.category, 'function')
        self.assertEqual(result.process_id, 5)
        self.assertEqual(result.thread_id, 10)
        self.assertEqual(result.timestamp, 10.0)
        self.assertEqual(result.args.get('foo'), 10)

    def test_complete_event_decode_with_defaults(self):
        # Arrange
        jsonStr = '{"name": "somename", "ph": "C", "ts": 10, "args": {"foo": 10}}'

        # Act
        result = loads(jsonStr, cls=TraceJsonDecoder)

        # Assert
        self.assertIsInstance(result, CounterEvent)
        self.assertEqual(result.name, 'somename')
        self.assertEqual(result.category, 'function')
        self.assertEqual(result.process_id, 0)
        self.assertEqual(result.thread_id, 0)
        self.assertEqual(result.timestamp, 10.0)
        self.assertEqual(result.args.get('foo'), 10)