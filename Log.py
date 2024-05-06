from datetime import datetime

class Log:
    def __init__(self):
        self.debug = False

    def enable_debug(self):
        self.debug = True

    def disable_debug(self):
        self.debug = False

    def is_debug(self):
        return self.debug

    def print(self, *args):
        if self.is_debug():
            now = datetime.now()
            dt_string = now.strftime("%H:%M:%S")
            print('[' + dt_string +']', *args)