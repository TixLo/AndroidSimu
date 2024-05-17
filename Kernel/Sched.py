import simpy
from Basic import Basic
from Kernel.SchedPolicy import SchedPolicy
from HW.CPU import CPU

class Sched(Basic):
    def __init__(self, *args, cfg, evt, **kwargs):
        super().__init__(*args, **kwargs)
        self.cfg = cfg
        self.evt = evt
        self.cpus = []
        self.pelt_n = cfg['pelt-n']
        self.cpufreq = None
        self.task_init_util = cfg['task_init_util']
        self.idle_prefer = cfg['idle_prefer']
        self.cpu_dispatch_bypass = cfg['cpu_dispatch_bypass']
        self.load_balance = cfg['load_balance']

        self.enable_debug()

        for i in range(len(self.cfg['cpus'])):
            # self.print(i, self.cfg[i])
            cpu = CPU(self.env, 'CPU', index=i, cfg=self.cfg['cpus'][i], evt=self.evt)
            if self.pelt_n == 32:
                cpu.decay_y = 0.97857206
            elif self.pelt_n == 16:
                cpu.decay_y = 0.95760328
            elif self.pelt_n == 8:
                cpu.decay_y = 0.91700404
            cpu.task_init_util = self.task_init_util
            cpu.fixed_freq = self.cfg['cpu_fixed_freq'][i]
            self.cpus.append(cpu)

        for i in cfg['cpu_off']:
            self.cpus[i].off = True
        
        self.policy = SchedPolicy(self.env, 'TinyEASPolicy', \
            cpus=self.cpus, task_init_util=self.task_init_util, idle_prefer=self.idle_prefer, \
            cpu_dispatch_bypass=self.cpu_dispatch_bypass)

    def dump(self):
        self.print('total CPUs :', len(self.cpus))
        for c in self.cpus:
            c.dump()

    def set_cpufreq(self, cpufreq):
        self.cpufreq = cpufreq
        for cpu in self.cpus:
            self.cpufreq.add(cpu.cluster)
            cpu.cpufreq = self.cpufreq
        self.cpufreq.cpus = self.cpus

    def put_tasks_into_cpu(self, curr_time, tasks):
        for t in tasks:
            index = self.policy.task_dispatch(t)
            cpu = self.cpus[index]
            cpu.inject_task(curr_time, t)


    def walk(self, curr_time, delta_time):
        for cpu in self.cpus:
            cpu.walk(curr_time, delta_time)

    def decay(self, curr_time):
        for cpu in self.cpus:
            cpu.decay(curr_time)

    def load_balance_push_migration(self, curr_time, cpu):
        if self.load_balance == True:
            self.policy.push_migration(curr_time, cpu)


