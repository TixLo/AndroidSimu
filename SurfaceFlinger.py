import simpy

from Basic import Basic

class SurfaceFlinger(Basic):
    def __init__(self, *args, vsync_dur, app_dur, sf_dur, **kwargs):
        super().__init__(*args, **kwargs)
        self.vsync_dur = vsync_dur
        self.app_dur = app_dur
        self.sf_dur = sf_dur

        # self.enable_debug()

        self.app_phase, self.sf_phase = self.calculate_app_sf_phase()

    def calculate_app_sf_phase(self):
        # calculate app/sf phase
        #https://android.googlesource.com/platform/frameworks/native/+/master/services/surfaceflinger/Scheduler/VsyncConfiguration.cpp
        vsync_dur_ns = int(self.vsync_dur * 1000000) #ms to ns
        app_dur_ns = int(self.app_dur * 1000000) #ms to ns
        sf_dur_ns = int(self.sf_dur * 1000000) #ms to ns
        self.print(vsync_dur_ns, app_dur_ns, sf_dur_ns)

        app_phase = vsync_dur_ns - (app_dur_ns + sf_dur_ns) % vsync_dur_ns
        sf_phase = vsync_dur_ns - (sf_dur_ns % vsync_dur_ns)
        self.print(app_phase, sf_phase)

        return float(app_phase / 1000000), float(sf_phase / 1000000)
       


        
