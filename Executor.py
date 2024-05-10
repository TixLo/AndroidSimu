import simpy
import time

from Basic import Basic
from Event import *
from UI.Console import Console
from Task import Task
from Trace import Trace
from Kernel.CpuFreq import CpuFreq

class Executor(Basic):
    def __init__(self, *args, evt, enable_console, **kwargs):
        super().__init__(*args, **kwargs)
        self.evt = evt
        self.sched = None
        self.curr_time = 0
        self.last_task = None
        self.trace = Trace(self.env, 'Trace')
        self.evt_loop_proc = self.env.process(self.evt_loop())
        self.cpufreq = CpuFreq(self.env, 'CpuFreq', evt=self.evt)
        self.final_countdown = 20

        self.console = None
        if enable_console == True:
            self.console = Console()
        # else:
        #     self.enable_debug()

    def set_sched(self, sched):
        self.sched = sched
        self.sched.set_cpufreq(self.cpufreq)

        if self.console != None:
            self.console.cpus = self.sched.cpus

    def set_task_data(self, data):
        self.task_json = data
        self.tasks = self.tasks_generator()

    def tasks_generator(self):
        for d in self.task_json:
            yield Task.import_from_json(d)

    def is_finished(self):
        completed_count = 0
        input_task_count = len(self.task_json)
        all_cpu_empty = True

        for c in self.sched.cpus:
            completed_count += len(c.completed_tasks)
            if c.is_empty() == False:
                all_cpu_empty = False
            # print('C%d, completed:%d, input_task_count: %d, all_cpu_empty: %d' % (c.index, completed_count, input_task_count, all_cpu_empty))

        remaining_tasks = input_task_count - completed_count
        if remaining_tasks == 0 and all_cpu_empty == True:
            return True
        else:
            return False

    def run(self, until):
        try:
            if until > 0:
                while self.env.peek() < until:
                    self.env.step()
            else:
                while True:
                    finish = False
                    self.env.peek()
                    self.env.step()
                    if self.is_finished() == True:
                        self.final_countdown -= 1
                        if self.final_countdown == 0:
                            finish = True
                    if finish == True:
                        break

        except KeyboardInterrupt:
            print('Ctrl-C to stop')

        # self.env.run(until)
        if self.console != None:
            self.console.finalized()

    def evt_loop(self):
        while True:
            data = yield self.evt.recv()
            if isinstance(data, TickEvent):
                # if data.name == 'tick':
                self.tick_evt_callback(data)
                if data.name == 'hw vsync':
                    self.hw_vsync_callback(data)
                elif data.name == 'sw vsync':
                    self.sw_vsync_callback(data)
                elif data.name == 'vsync-app':
                    self.vsync_app_callback(data)
                elif data.name == 'vsync-sf':
                    self.vsync_sf_callback(data)
                elif data.name == 'cpufreq':
                    self.cpufreq.update_freq(data.timestamp)
                else:
                    # 1ms periodically trigger
                    self.sched.decay(data.timestamp)
            elif isinstance(data, TaskCompletedEvent):
                self.task_completed_callback(data.task)
            elif isinstance(data, CpuFreqEvent):
                self.cpu_freq_change_callback(data.timestamp, data.freqs)

            # update the console and this code should be the last in the while loop    
            if self.console != None:
                # if self.sched != None:
                #     self.sched.update_console(self.console)

                if self.task_json != None:
                    self.console.input_task_count = len(self.task_json)
                self.console.update()


    def tick_evt_callback(self, data):
        delta_time = data.timestamp - self.curr_time
        if delta_time == 0:
            return
        self.print('Execotur got tick event, timestamp: %.6f s, delta: %.6f s' % (self.curr_time, delta_time))
        
        #
        # load tasks between [self.curr_time, self.curr_time + delta_time]
        #
        ready_tasks = self.load_tasks(self.curr_time, delta_time)
        if len(ready_tasks) > 0:
            # put ready_tasks into runnable queue of scheduler
            self.sched.put_tasks_into_cpu(self.curr_time, ready_tasks)

        #
        # Scheduler walk the delta time
        #
        # self.print('curr_time: %.6f, delta_time: %.6f' % (self.curr_time, delta_time))
        self.sched.walk(self.curr_time, delta_time)

        #
        # update current time
        #
        #update console
        if self.console != None:
            self.console.curr_time = (data.timestamp * 1000) #convert to ms
            self.console.delta_time = (delta_time * 1000) #convert to ms

        self.curr_time = data.timestamp

    def hw_vsync_callback(self, data):
        self.print('Execotur got hw vsync event, timestamp: %.6f s' % (data.timestamp))
        if self.console != None:
            self.console.tick_evts['HW VSYNC'] = data.timestamp * 1000 # convert to ms

    def sw_vsync_callback(self, data):
        self.print('Execotur got sw vsync event, timestamp: %.6f s' % (data.timestamp))
        if self.console != None:
            self.console.tick_evts['SW VSYNC'] = data.timestamp * 1000 # convert to ms

    def vsync_app_callback(self, data):
        self.print('Execotur got vsync-app event, timestamp: %.6f s' % (data.timestamp))
        if self.console != None:
            self.console.tick_evts['vsync-app'] = data.timestamp * 1000 # convert to ms

    def vsync_sf_callback(self, data):
        self.print('Execotur got vsync-sf event, timestamp: %.6f s' % (data.timestamp))
        if self.console != None:
            self.console.tick_evts['vsync-sf'] = data.timestamp * 1000 # convert to ms

    def task_completed_callback(self, task):
        self.print('tasl_completed_callback')
        task.dump()
        self.trace.inject(task)

    def cpu_freq_change_callback(self, timestamp, freqs):
        self.trace.inject_cpu_freq(timestamp, freqs)

    def load_tasks(self, start_ts, duration):
        ready_tasks = []
        # self.print('start_ts: %.6f, end_ts: %.6f' % (start_ts, start_ts + duration))

        if self.last_task != None:
            if self.last_task.ts >= start_ts and self.last_task.ts < start_ts + duration:
                ready_tasks.append(self.last_task)
            else:
                return ready_tasks

        for t in self.tasks:
            # t.dump()
            if t.ts >= start_ts and t.ts < start_ts + duration:
                ready_tasks.append(t)
            else:
                self.last_task = t
                break

        return ready_tasks

    def save(self, filename):
        self.trace.save(filename)