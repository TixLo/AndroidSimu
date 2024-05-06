from datetime import datetime

from Log import Log

class Basic:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.log = Log()

    def enable_debug(self):
        self.log.enable_debug()

    def disable_debug(self):
        self.log.disable_debug()

    def is_debug(self):
        return self.log.is_debug()

    def print(self, *args):
        self.log.print(*args)
