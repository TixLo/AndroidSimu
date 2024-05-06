import simpy

from Basic import Basic
from Tick import Tick
from SurfaceFlinger import SurfaceFlinger
from Executor import Executor
from Event import Event
from Kernel.Sched import Sched

class Android(Basic):
    def __init__(self, *args, cfg, **kwargs):
        super().__init__(*args, **kwargs)
        self.evt = Event(self.env)
        self.hw_vsync_interval = 16.6
        self.cfg = cfg
        
        self.enable_debug()

    def set_task_data(self, data):
        self.task_json = data

    def run(self, until):
        self.exec.run(until)

    def boot(self):
        self.print('start booting Android System')

        #
        # create SurfaceFlinger module
        #
        self.print('creating SurfaceFlinger module')
        self.sf = SurfaceFlinger(self.env, 'SF',
            vsync_dur=self.hw_vsync_interval, app_dur=20.5, sf_dur=10.5)
        self.print('-> app_phase: %.1f ms, sf_phase: %.1f ms' % (self.sf.app_phase, self.sf.sf_phase))

        #
        # create Scheduler module
        #
        self.sched = Sched(self.env, 'TinySched', cfg=self.cfg['sched'], evt=self.evt)
        self.sched.dump()

        #
        # create Executor module
        #
        self.print('creating Executor module')
        self.exec = Executor(self.env, 'Executor', evt=self.evt,
            enable_console=self.cfg['android']['executor_console'])
        self.exec.set_sched(self.sched)
        self.exec.set_task_data(self.task_json)

        #
        # create tick events
        #
        self.print('Create tick modules, including tick, HW Vsync, ...etc')
        self.create_ticks()

    def create_ticks(self):
        self.tick = Tick(self.env, 'tick', interval=1.0, delay=0.0, evt=self.evt)
        # self.tick.enable_debug()

        self.hw_vsync = Tick(self.env, 'hw vsync', 
            interval=self.hw_vsync_interval, delay=0.0, evt=self.evt)
        # self.hw_vsync.enable_debug()

        self.sw_vsync = Tick(self.env, 'sw vsync', 
            interval=self.hw_vsync_interval, delay=0.0, evt=self.evt)
        # self.sw_vsync.enable_debug()
        
        self.vsync_app = Tick(self.env, 'vsync-app', 
            interval=self.hw_vsync_interval, delay=self.sf.app_phase, evt=self.evt)
        # self.vsync_app.enable_debug()
        
        self.vsync_sf = Tick(self.env, 'vsync-sf', 
            interval=self.hw_vsync_interval, delay=self.sf.sf_phase, evt=self.evt)
        # self.vsync_sf.enable_debug()

        self.cpu_freq = Tick(self.env, 'cpufreq', interval=1.0, delay=0.0, evt=self.evt)
        # self.vsync_sf.enable_debug()

    def to_trace(self, filename):
        self.exec.save(filename)

