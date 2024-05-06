import simpy
from Basic import Basic
from Event import *

class CpuFreq(Basic):
    def __init__(self, *args, evt, **kwargs):
        super().__init__(*args, **kwargs)
        self.evt = evt
        self.freqs = []
        self.cpus = None

        self.enable_debug()

    def add(self, cluster):
        self.freqs.append({'freq': 0, 'cluster': cluster})

    def update_freq(self, curr_time):
        # self.print('update cpu freq, %.6f' % curr_time)
        freq_cluster_map = {}
        for index in range(len(self.freqs)):
            item = self.freqs[index]
            # self.print('CPU%d, freq:%d' % (index, item['freq']))

            if item['cluster'] not in freq_cluster_map:
                freq_cluster_map[item['cluster']] = -1

            freq_cluster_map[item['cluster']] = max(freq_cluster_map[item['cluster']], item['freq'])            
            
        # for k, v in freq_cluster_map.items():
        #     self.print('freq_cluster_map[%d]: %d' % (k, v))

        for cpu in self.cpus:
            cpu.change_freq(freq_cluster_map[cpu.cluster])

        # send freq data to Executor and export to trace file
        self.send_freq_evt(curr_time, freq_cluster_map)

    def send_freq_evt(self, curr_time, freq_cluster_map):
        data = []
        for cpu in self.cpus:
            data.append(freq_cluster_map[cpu.cluster])

        freq_evt = CpuFreqEvent(timestamp=curr_time, freqs=data)
        self.evt.send(freq_evt)

    def set_freq(self, index, freq):
        self.freqs[index]['freq'] = freq
