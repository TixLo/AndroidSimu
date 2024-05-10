import simpy
import math

from Basic import Basic
from Task import Task
from Event import *
from Kernel.PowerTable import PowerTable
from Kernel.CpuFreq import CpuFreq

class CPU(Basic):
    def __init__(self, *args, index, cfg, evt, **kwargs):
        super().__init__(*args, **kwargs)
        self.cfg = cfg
        self.evt = evt
        self.index = index
        self.max_freq = cfg['max_freq'] # MHz
        self.freq = 0 # MHz
        self.ipc = cfg['ipc']
        self.runnable = []
        self.task = None
        self.completed_tasks = []
        self.consumed_workload = 0
        self.util = 0
        self.decay_y = 0
        self.decay_ts = 0
        self.consuming_time = 0
        self.cluster = cfg['cluster']
        self.pwr_tbl = None
        self.cpufreq = None
        self.off = False
        self.fixed_freq = -1
        self.fixed_freq_launch_event = False

        self.enable_debug()

    def dump(self):
        self.print('[%d]CPU%d, freq: %d MHz, max_freq: %d MHz, ipc: %.2f, util: %d, y: %.6f, off: %d' % 
            (self.cluster, self.index, self.freq, self.max_freq, self.ipc, self.util, self.decay_y, self.off))

    def is_empty(self):
        if len(self.runnable) == 0 and self.task == None:
            return True
        else:
            return False

    def inject_task(self, curr_time, task):
        task.rt_inject_ts = curr_time
        if self.task == None:
            self.task = task
            self.task.rt_cpu = self.index
            self.task.rt_b_ts = curr_time
        else:
            self.runnable.append(task)

    def walk(self, curr_time, delta_time):
        if self.task != None:
            task_end_ts, remaining_time = self.consume_workload(curr_time, delta_time, self.task)
            # print('task_end_ts: %.6f, remaining_time: %.6f' % (task_end_ts, remaining_time))

            if remaining_time == 0:
                return            

            while True:
                if len(self.runnable) == 0:
                    break

                self.task = self.runnable.pop(0)
                self.task.rt_b_ts = task_end_ts
                self.task.rt_cpu = self.index
                # self.task.dump()
                task_end_ts, remaining_time = self.consume_workload(task_end_ts, remaining_time, self.task)
                # print('task_end_ts: %.6f, remaining_time: %.6f' % (task_end_ts, remaining_time))
                # input()
                if remaining_time == 0:
                    return

    def consume_workload(self, curr_time, delta_time, task):
        if self.fixed_freq == -1:
            self.consumed_workload = delta_time * self.freq * 1000000 * self.ipc
        else:
            self.consumed_workload = delta_time * self.fixed_freq * 1000000 * self.ipc
        # print('delta_time: %.6f, self.freq: %d, self.ipc: %.2f, consumed_workload: %d' % (delta_time, self.freq, self.ipc, self.consumed_workload))
        # task.dump()

        task.rt_workload = task.rt_workload - self.consumed_workload
        if task.rt_workload <= 0:
            remaining_time = (task.rt_workload / self.consumed_workload) * delta_time
            # print('remaining_time: %.6f, rt_workload: %d' % (remaining_time, task.rt_workload))
            task_end_ts = curr_time + delta_time + remaining_time # remaining_time is negative
            task.rt_e_ts = task_end_ts
            task.rt_dur = task.rt_e_ts - task.rt_b_ts
            task.rt_workload = 0

            self.consuming_time += (delta_time + remaining_time)
            self.completed_tasks.append(task)
            self.task = None

            # send completed event to Executor loop
            task_evt = TaskCompletedEvent(task=task)
            self.evt.send(task_evt)

            return task_end_ts, -remaining_time
        else:
            self.consuming_time += delta_time
            return 0, 0

    def decay(self, curr_time):
        if self.util == 0 and self.consuming_time == 0:
            return
        # self.print('decay: %.6f, consuming_time: %.6f' % (curr_time, self.consuming_time))
        #
        # decay formula
        # loading = consuming time / 1ms
        # new util = Max. Capacity * (1 - y) * loading + old util * y
        #
        new_util = round(1024 * (1.0 - self.decay_y) * (self.consuming_time * 1000) + self.util * self.decay_y)
        self.consuming_time = 0
        if new_util > 0 and new_util == self.util:
            new_util -= 1
        # self.print('new_util: %d, old_util:%d' % (new_util, self.util))
        self.util = new_util

        if self.fixed_freq == -1:
            # get CPU frequency in according to power_table
            index, freq = self.pwr_tbl.get_freq(self.util, 0.8)
            # self.print('new util: %d, req: %d' % (self.util, freq))
            self.cpufreq.set_freq(self.index, freq)
        elif self.fixed_freq_launch_event == False:
            self.cpufreq.set_freq(self.index, self.fixed_freq)
            self.fixed_freq_launch_event = True
        # input()

    def change_freq(self, new_freq):
        # self.print('change freq from %d to %d' % (self.freq, new_freq))
        self.freq = new_freq


