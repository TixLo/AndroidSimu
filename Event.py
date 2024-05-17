import simpy

class Event:
    def __init__(self, env):
        self.env = env
        self.store = simpy.Store(env)

    def latency(self, value, delay):
        yield self.env.timeout(delay)
        self.store.put(value)

    def send(self, value, delay=0):
        if delay == 0:
            self.store.put(value)
        else:
            self.env.process(self.latency(value, delay))

    def recv(self):
        return self.store.get()

class TickEvent:
    def __init__(self, name, timestamp):
        self.name = name
        self.timestamp = timestamp

class TaskCompletedEvent:
    def __init__(self, task):
        self.task = task

class CpuFreqEvent:
    def __init__(self, timestamp, freqs):
        self.timestamp = timestamp
        self.freqs = freqs

class PushMigrationEvent:
    def __init__(self, timestamp, cpu):
        self.timestamp = timestamp
        self.cpu = cpu


        
