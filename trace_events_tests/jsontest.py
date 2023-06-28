from json import dumps, loads
from os import getpid
from threading import current_thread
import unittest

from trace_events.events import CompleteEvent
from trace_events.json import TraceJsonDecoder, TraceJsonEncoder


class TraceJsonEncoderTests(unittest.TestCase):

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

    def test_complete_event_decode(self):
        # Arrange
        jsonStr = '{"name": "somename", "cat": "function", "ph": "X", "pid": 5, "tis": 10, "ts": 10, "dur": 42}'

        # Act
        result = loads(jsonStr, cls=TraceJsonDecoder)

        # Assert
        self.assertIsInstance(result, CompleteEvent)
        self.assertEqual(result.name, 'somename')
        self.assertEqual(result.category, 'function')
        # self.assertEqual(result.event_type, 'X')
        self.assertEqual(result.process_id, 5)
        self.assertEqual(result.thread_id, 10)
        self.assertEqual(result.start_time, 10.0)
        self.assertEqual(result.duration, 42.0)

    def test_complete_event_decode_with_defaults(self):
        # Arrange
        jsonStr = expected = '{"name": "somename", "ph": "X", "ts": 10, "dur": 42}'

        # Act
        result = loads(jsonStr, cls=TraceJsonDecoder)

        # Assert
        self.assertIsInstance(result, CompleteEvent)
        self.assertEqual(result.name, 'somename')
        self.assertEqual(result.category, 'function')
        # self.assertEqual(result.event_type, 'X')
        self.assertEqual(result.process_id, 0)
        self.assertEqual(result.thread_id, 0)
        self.assertEqual(result.start_time, 10.0)
        self.assertEqual(result.duration, 42.0)