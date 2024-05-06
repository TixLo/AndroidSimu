import simpy
from Basic import Basic
from HW.CPU import CPU
from Kernel.PowerTable import PowerTable

class SchedPolicy(Basic):
    def __init__(self, *args, cpus, **kwargs):
        super().__init__(*args, **kwargs)
        self.cpus = cpus
        self.create_eas_power_table()

        for cpu in self.cpus:
            cpu.freq = cpu.max_freq
            if cpu.cluster == 0:
                cpu.pwr_tbl = self.l_pwr_tbl
            elif cpu.cluster == 1:
                cpu.pwr_tbl = self.m_pwr_tbl
            elif cpu.cluster == 2:
                cpu.pwr_tbl = self.b_pwr_tbl

        self.enable_debug()

    def create_eas_power_table(self):
        self.l_pwr_tbl = PowerTable(self.env, 'LCPU Power Table')
        self.l_pwr_tbl.append( 300,  70, 10000)
        self.l_pwr_tbl.append( 500, 110, 12000)
        self.l_pwr_tbl.append( 800, 150, 15000)
        self.l_pwr_tbl.append(1100, 220, 18000)
        self.l_pwr_tbl.append(1400, 270, 25000)
        self.l_pwr_tbl.append(1600, 310, 35000)
        self.l_pwr_tbl.append(1900, 350, 48000)
        self.l_pwr_tbl.dump()

        self.m_pwr_tbl = PowerTable(self.env, 'MCPU Power Table')
        self.m_pwr_tbl.append( 800, 220, 22000)
        self.m_pwr_tbl.append(1200, 300, 25000)
        self.m_pwr_tbl.append(1500, 380, 32000)
        self.m_pwr_tbl.append(1800, 460, 37000)
        self.m_pwr_tbl.append(2100, 540, 49000)
        self.m_pwr_tbl.append(2500, 620, 63000)
        self.m_pwr_tbl.append(2850, 700, 80000)
        self.m_pwr_tbl.dump()

        self.b_pwr_tbl = PowerTable(self.env, 'BCPU Power Table')
        self.b_pwr_tbl.append(1200, 400, 46000)
        self.b_pwr_tbl.append(1500, 500, 50000)
        self.b_pwr_tbl.append(1800, 600, 55000)
        self.b_pwr_tbl.append(2100, 700, 62000)
        self.b_pwr_tbl.append(2500, 800, 72000)
        self.b_pwr_tbl.append(2800, 900, 91000)
        self.b_pwr_tbl.append(3200,1024, 125000)
        self.b_pwr_tbl.dump()

    def task_dispatch(self, task):
        return task.cpu
