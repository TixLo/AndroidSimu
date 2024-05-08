import simpy

from Basic import Basic

class PowerTable(Basic):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = []

        self.enable_debug()

    def append(self, freq, cap, power):
        self.data.append({
            'index': len(self.data),
            'freq': freq,
            'cap': cap,
            'power': power
        })

    def dump(self):
        self.print('dump power table: %s' % self.name)
        for i in range(len(self.data)):
            pwr = self.data[i]
            self.print('[%d] freq: %d MHz, cap: %d, power: %d' % (pwr['index'], pwr['freq'], pwr['cap'], pwr['power']))

    def get_freq(self, cap, threshold):
        freq = self.data[0]['freq']
        index = self.data[0]['index']
        # self.print('max freq: %d, input cap: %d, threshold: %.1f' % (freq, cap, threshold))
        for item in self.data:
            # self.print('cap: %d > %d?' % (cap, item['cap'] * threshold))
            if cap > item['cap'] * threshold:
                freq = item['freq']
                index = item['index']
                # self.print('update freq: %d' % freq)
            else:
                break
        return index, freq
