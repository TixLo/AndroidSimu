import simpy
from Basic import Basic
from HW.CPU import CPU
from Kernel.PowerTable import PowerTable

class SchedPolicy(Basic):
    def __init__(self, *args, cpus, task_init_util, idle_prefer, cpu_dispatch_bypass, **kwargs):
        super().__init__(*args, **kwargs)
        self.cpus = cpus
        self.task_init_util = task_init_util
        self.idle_prefer = idle_prefer
        self.cpu_dispatch_bypass = cpu_dispatch_bypass
        self.create_eas_power_table()

        for cpu in self.cpus:
            cpu.freq = cpu.max_freq
            if cpu.cluster == 0:
                cpu.pwr_tbl = self.l_pwr_tbl
            elif cpu.cluster == 1:
                cpu.pwr_tbl = self.m_pwr_tbl
            elif cpu.cluster == 2:
                cpu.pwr_tbl = self.b_pwr_tbl

        # self.enable_debug()

    def create_eas_power_table(self):
        self.l_pwr_tbl = PowerTable(self.env, 'LCPU Power Table')
        self.l_pwr_tbl.append( 300,  70, 10000)
        self.l_pwr_tbl.append( 500, 110, 12000)
        self.l_pwr_tbl.append( 800, 150, 15000)
        self.l_pwr_tbl.append(1100, 220, 18000)
        self.l_pwr_tbl.append(1400, 270, 25000)
        self.l_pwr_tbl.append(1600, 310, 35000)
        self.l_pwr_tbl.append(1900, 350, 58000)
        self.l_pwr_tbl.dump()

        self.m_pwr_tbl = PowerTable(self.env, 'MCPU Power Table')
        self.m_pwr_tbl.append( 800, 220, 24000)
        self.m_pwr_tbl.append(1200, 300, 27000)
        self.m_pwr_tbl.append(1500, 380, 34000)
        self.m_pwr_tbl.append(1800, 460, 39000)
        self.m_pwr_tbl.append(2100, 540, 56000)
        self.m_pwr_tbl.append(2500, 620, 70000)
        self.m_pwr_tbl.append(2850, 700, 89000)
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
        if self.cpu_dispatch_bypass == True:
            selected_cpu = task.cpu
        else:
            powers = {}

            for c in range(len(self.cpus)):
                powers[c] = 0
                self.print('---- try to put task to CPU:%d -----' % c)
                #
                # assign a large fake power to off cpu
                # 
                if self.cpus[c].off == True:
                    powers[c] = 99999999
                else:
                    for cpu in self.cpus:
                        util = cpu.util
                        if c == cpu.index:
                            util += self.task_init_util

                        index, freq = cpu.pwr_tbl.get_freq(util, 0.8)
                        ratio = (util / cpu.pwr_tbl.data[index]['cap'])
                        expected_power = int(cpu.pwr_tbl.data[index]['power'] * ratio)
                        self.print('[%d] util: %d, init util: %d, cpu util: %d, cap: %d, ratio: %.2f' % (c, util, self.task_init_util, cpu.util, cpu.pwr_tbl.data[index]['cap'], ratio))
                        self.print('[%d] index: %d, freq: %d, expected power: %d' % (c, index, freq, expected_power))
                        powers[c] += expected_power

            for k, v in powers.items():
                self.print('put cpu %d and power: %d' % (k, v))
            #
            # check all cpus are running?
            #
            all_running = True
            for cpu in self.cpus:
                if cpu.task == None:
                    all_running = False
                    break

            #
            # selection rules:
            # 1. choose the most efficiency CPU if idle_prefer = False
            # 2. choose the efficiency and idle CPU if idle_prefer = True
            # 3. choose the most efficiency CPU if idle_prefer = False and all cpu are running
            #
            selected_cpu = -1
            sorted_powers = sorted(powers.items(), key=lambda x:x[1])
            for index, power in sorted_powers:
                # self.print('CPU%d, power: %d' % (index, power))
                if self.idle_prefer == False or all_running:
                    selected_cpu = index
                    break
                else:
                    for cpu in self.cpus:
                        if cpu.task == None:
                            selected_cpu = cpu.index
                            break
                    if selected_cpu != -1:
                        break
                            
        # self.print('selected_cpu: %d, idle_prefer: %d, bypass: %d' % (selected_cpu, self.idle_prefer, self.cpu_dispatch_bypass))
        # input()
        return selected_cpu

    def push_migration(self, curr_time, cpu):
        if len(cpu.runnable) == 0:
            return

        # 1. get the next task on busy CPU
        task = cpu.runnable[0]

        # 2. find the most CPU power efficiency combinarion
        selected_cpu = self.task_dispatch(task)
        self.print('selected cpu: %d' % selected_cpu)

        # 3. only handle the task changing the CPU case
        if selected_cpu != cpu.index:
            # inject task to another CPU
            self.print('inject task to another CPU: %d' % selected_cpu)
            self.cpus[selected_cpu].inject_task(curr_time, task)

            # remove the task from original CPU
            cpu.runnable.pop()
        # input()

