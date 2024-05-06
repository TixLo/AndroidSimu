import simpy
import os
import sys

from Basic import Basic
from MultiMap import MultiMap
from Task import Task

class Trace(Basic):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.multimap = MultiMap()

        self.enable_debug()

    def inject(self, task):
        lines = task.to_trace()
        for line in lines:
            ts = line['ts']
            text = line['trace']
            self.multimap[ts] = text

    def inject_cpu_freq(self, timestamp, freqs):
        for index in range(len(freqs)):
            freq = freqs[index]
            if freq == 0:
                continue
            cpu_frequency = '<idle>-0     (-----) [%.3d] .... %.6f: cpu_frequency: state=%d cpu_id=%d' \
                    % (index, timestamp, freq * 1000, index)
            self.multimap[timestamp] = cpu_frequency

    def dump(self):
        for lines in self.multimap.values():
            for line in lines:
                print(line)

    def trace_generator(self):
        for lines in self.multimap.values():
            for line in lines:
                yield line + '\n'

    def save(self, filename):
        trace_header = '''# tracer: nop
#
# entries-in-buffer/entries-written: 30624/30624   #P:4
#
#                                      _-----=> irqs-off
#                                     / _----=> need-resched
#                                    | / _---=> hardirq/softirq
#                                    || / _--=> preempt-depth
#                                    ||| /     delay
#           TASK-PID    TGID   CPU#  ||||    TIMESTAMP  FUNCTION
#              | |        |      |   ||||       |         |
'''
        file = open(filename, 'w')
        file.writelines(trace_header)
        for line in self.trace_generator():
            file.write(line)
        file.close()
 
