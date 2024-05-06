import simpy
import math
import time

from Basic import Basic
from Event import *

class Tick(Basic):
    def __init__(self, *args, interval, delay, evt, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale = 10 #0.1ms granularity
        self.interval = interval * self.scale
        self.delay = delay * self.scale
        self.evt = evt
        self.timestamp = 0

        self.boot_proc = self.env.process(self.loop())
        self.enable_debug()

    def loop(self):
        yield self.env.timeout(self.delay)
        while True:
            yield self.env.timeout(self.interval)
            self.timestamp = self.env.now

            # self.print_timestamp()
            tick_evt = TickEvent(name=self.name, timestamp=self.get_timestamp())
            self.evt.send(tick_evt)

    def print_timestamp(self):
        if self.is_debug() == False:
            return
        factor = self.scale * 1000
        millis = self.timestamp % factor
        seconds = int(self.timestamp / factor) % 60
        minutes = int(self.timestamp / (factor * 60)) % 60
        hours = int(self.timestamp / (factor * 60 * 60)) % 24
        
        self.print('%s is triggerd at timestamp %d:%d:%d.%.4d' % (self.name, hours, minutes, seconds, millis))

    def get_timestamp(self):
        return (self.timestamp / self.scale) / 1000.0 #convert to second