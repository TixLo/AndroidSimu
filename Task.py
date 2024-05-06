import simpy
import json

from Basic import Basic
from Log import Log

class Task(Log):
    def __init__(self):
        super().__init__()

        # traced_probes-25434 (25434) [003] .... 261187.012114: task_newtask: oom_score_adj=-1000 comm=traced_probes pid=20614 clone_flags=4001536
        #task basic information
        self.id = 0
        self.name = ''
        self.pid = 0
        self.tgid = 0
        self.cpu = -1
        self.ts = 0.0
        self.dur = 0.0

        #task runtime information
        self.rt_inject_ts = 0
        self.rt_b_ts = 0
        self.rt_e_ts = -1
        self.rt_dur = 0
        self.rt_workload = -1 #workload = freq * execution time * IPC
        self.rt_util = 0

        self.enable_debug()

    @staticmethod
    def import_from_json(data):
        task = Task()
        task.id = data['id']
        task.name = data['name']
        task.pid = data['pid']
        task.tgid = data['tgid']
        task.cpu = data['cpu']
        task.ts = data['ts']
        task.dur = data['dur']
        task.rt_workload = data['workload']
        return task

    def get_key(self):
        return '%d_%.6f' % (self.id, self.ts)

    def dump(self):
        self.print('task name: %s, pid: %d, tgid: %d, cpu: %d, ts: %.6f, dur: %.6f, wl: %d' %
            (self.name, self.pid, self.tgid, self.cpu, self.ts, self.dur, self.rt_workload))

    def dump_rt(self):
        self.print('task name: %s, pid: %d, tgid: %d, cpu: %d, inject_ts: %.6f, b_ts: %.6f, e_ts: %.6f, dur: %.6f, wl: %d' %
            (self.name, self.pid, self.tgid, self.cpu, self.rt_inject, self.rt_b_ts, self.rt_e_ts, self.rt_dur, self.rt_workload))

    def to_trace(self):
        traces = []
        #traced_probes-25434 (25434) [003] .... 261187.012442: sched_wakeup: comm=traced_probes pid=20614 prio=120 target_cpu=000
        #
        # generate sched_wakeup trace
        #
        sched_wakeup = '<idle>-0     (-----) [%.3d] .... %.6f: sched_wakeup: comm=%s pid=%d prio=120 target_cpu=%.3d' \
                % (self.cpu, self.rt_inject_ts, self.name, self.pid, self.cpu)
        # self.print(sched_wakeup)
        traces.append({'ts': self.rt_inject_ts, 'trace': sched_wakeup})

        #<idle>-0     (-----) [000] .... 261187.012454: sched_switch: prev_comm=swapper/0 prev_pid=0 prev_prio=120 prev_state=R ==> next_comm=traced_probes next_pid=20614 next_prio=120
        #
        # generate sched_switch start
        #
        sched_switch_s = '<idle>-0     (-----) [%.3d] .... %.6f: sched_switch: prev_comm=swapper/%d prev_pid=0 prev_prio=120 prev_state=R ==> next_comm=%s next_pid=%d next_prio=120' \
                % (self.cpu, self.rt_b_ts, self.cpu, self.name, self.pid)
        # self.print(sched_wakeup)
        traces.append({'ts': self.rt_b_ts, 'trace': sched_switch_s})

        #traced_probes0-20614 (25434) [000] .... 261187.012485: sched_switch: prev_comm=traced_probes prev_pid=20614 prev_prio=120 prev_state=D ==> next_comm=swapper/0 next_pid=0 next_prio=120
        #
        # generate sched_switch end
        #
        sched_switch_e = '%s-%d     (%d) [%.3d] .... %.6f: sched_switch: prev_comm=%s prev_pid=%d prev_prio=120 prev_state=D ==> next_comm=swapper/%d next_pid=0 next_prio=120' \
                % (self.name, self.pid, self.tgid, self.cpu, self.rt_e_ts, self.name, self.pid, self.cpu)
        # self.print(sched_switch_e)
        traces.append({'ts': self.rt_e_ts, 'trace': sched_switch_e})
        
        return traces


