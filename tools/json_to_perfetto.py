#!env python

import click
import json
import os
import random
import sys

from perfetto.trace_processor import TraceProcessor
import perfetto_trace_pb2 as perfetto_trace


def gen_uuid(bits=64):
    return int(random.getrandbits(bits))


@click.group()
def trace_tools():
    pass


@trace_tools.command()
@click.argument("json_file", type=click.File("r"), default=sys.stdin)
@click.argument("output", type=click.File("wb"))
def convert(json_file, output):
    with json_file:
        trace = json.load(json_file)

    pids = set([event["pid"] for event in trace["traceEvents"]])
    pid_tids = dict()
    for event in trace["traceEvents"]:
        if event["tis"] not in pid_tids:
            pid_tids[event["tis"]] = {"pid": event["pid"], "tid": event["tis"]}

    procs = {pid: {"pid": pid, "uuid": gen_uuid()} for pid in pids}
    threads = {pid_tid["tid"]: {"pid": pid_tid["pid"], "tid": pid_tid["tid"], "uuid": gen_uuid(), "seq_id": gen_uuid(32)} for pid_tid in pid_tids.values()}

    trace_msg = perfetto_trace.Trace()

    with output:
        for proc in procs.values():
            pkt = trace_msg.packet.add()
            pkt.track_descriptor.uuid = proc["uuid"]
            pkt.track_descriptor.process.pid = proc["pid"]
            pkt.track_descriptor.process.process_name = f"Process {proc['pid']}"

        for thd in threads.values():
            pkt = trace_msg.packet.add()
            pkt.track_descriptor.uuid = thd["uuid"]
            pkt.track_descriptor.parent_uuid = procs[thd["pid"]]["uuid"]
            pkt.track_descriptor.thread.pid = thd["pid"]
            pkt.track_descriptor.thread.tid = thd["tid"]
            pkt.track_descriptor.thread.thread_name = f"Thread {thd['tid']}"

        adjust = None

        for event in trace["traceEvents"]:
            pkt = trace_msg.packet.add()
            start = int(event["ts"] * 1e3)
            if start < 0:
                if adjust is None:
                    adjust = -start
                else:
                    raise Exception("more than one negative timestamp")
            start = start + adjust
            pkt.timestamp = start
            pkt.track_event.type = perfetto_trace.TrackEvent.Type.TYPE_SLICE_BEGIN
            pkt.track_event.track_uuid = threads[event["tis"]]["uuid"]
            pkt.track_event.name = event["name"]
            pkt.track_event.categories.append(event['cat'])
            pkt.trusted_packet_sequence_id = threads[event["tis"]]["seq_id"]

            pkt = trace_msg.packet.add()
            end = start + int(event["dur"]*1e3)
            pkt.timestamp = end
            pkt.track_event.type = perfetto_trace.TrackEvent.Type.TYPE_SLICE_END
            pkt.track_event.track_uuid = threads[event["tis"]]["uuid"]
            pkt.trusted_packet_sequence_id = threads[event["tis"]]["seq_id"]

        output.write(trace_msg.SerializeToString())


@trace_tools.command()
@click.argument("trace_file", type=click.File("r"), default=sys.stdin)
def check(trace_file):
    with trace_file:
        TraceProcessor(trace_file)


if __name__ == '__main__':
    pycharm_port = os.environ.get("PYCHARM_PORT")
    if pycharm_port is not None:
        pycharm_port = int(pycharm_port)
        import pydevd_pycharm

        pydevd_pycharm.settrace(
            "localhost", port=pycharm_port, stdoutToServer=True, stderrToServer=True
        )

    trace_tools()
