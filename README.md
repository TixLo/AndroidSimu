## AndroidSimu is a task-based simulator of Android system.
### How to use
- install SimPy package
- git clone project
- python main.py

Here are two important json configuration.
- Simulator config
```
    configs = {
        'android': {
            'executor_console': False 
        },
        'sched': {
            'cpus': [
                { 'max_freq': 1900, 'ipc': 0.9, 'cluster': 0},
                { 'max_freq': 2850, 'ipc': 1.2, 'cluster': 1},
                { 'max_freq': 3200, 'ipc': 1.6, 'cluster': 2}
            ],
            'pelt-n': 8,
            'cpu_dispatch_bypass': False,
            'idle_prefer': False,
            'task_init_util': 128,
            'load_balance': True,
            'cpu_off': [],
            'cpu_fixed_freq': [-1, -1, -1]
        }
    }
```
  - android:executor_console, False: text mode, True: visualization mode
  - sched:cpus, CPU architecture definitation
  - sched:pelt-n, set the scheduler load tracking behavior, 32/16/8 are supported currently
  - sched:cpu_dispatch_bypass, dispatched cpu = original cpu
  - sched:idle_prefer, performance favor, dispatch any avaliable cpu
  - sched:task_init_util, initial capacity of a new task and the value will be used by EAS
  - sched:load_balance, enable load balancing mechanism implemend by push migration methodology
  - sched: cpu_off: which cpu can be turned off, e.g., [0, 2] --> turn off CPU0, CPU2
  - sched: cpu_fixed_freq: fixed cpu frequency
- Task config
```
{
        'id': 1,
        'name': 'A',
        'pid': 111,
        'tgid': 222,
        'cpu': 0,
        'ts': 0.001000,
        'dur': 1.500000,
        'workload': 5130000 #instructions = 1000 MHz * 0.001ms * 1.2 IPC
    }
```
  - id, the unique id
  - name, task name
  - pid, task thread id
  - tgid, task process id
  - cpu, which cpu is task running on
  - ts, the begin timestamp
  - dur, the execution time
  - workload, workload instruction count = CPU Freq(MHz) * exxecution time * IPC

  
There are two different exxecution mode. One is text mode and the other is visualization mode.

## text mode
```
tixlo:AndroidSimu tixlo$ python main.py 
[21:34:15] start booting Android System
[21:34:15] creating SurfaceFlinger module
[21:34:15] -> app_phase: 2.2 ms, sf_phase: 6.1 ms
[21:34:15] dump power table: LCPU Power Table
[21:34:15] [0] freq: 300 MHz, cap: 70, power: 10000
[21:34:15] [1] freq: 500 MHz, cap: 110, power: 12000
[21:34:15] [2] freq: 800 MHz, cap: 150, power: 15000
```
## visualization mode
```
Current Time: 9.00 ms, Walk Time: 1.00 ms, Remaining Task Count: 3
----------------------------------------------------------------------------------------------------------------------------------------------
CPU0, util: 163, task: A, workload: 2160000, consumed: 719999, Util: 163, freq: 800 MHz, runnableQ: 0, completed: 0
CPU1, util: 105, task: C, workload: 1290000, consumed: 959999, Util: 105, freq: 800 MHz, runnableQ: 0, completed: 0
CPU2, util: 22, task: C, workload: 5130000, consumed: 0, Util: 22, freq: 0 MHz, runnableQ: 0, completed: 0


----------------------------------------------------------------------------------------------------------------------------------------------
 CPU0 |                                                                                 ███████████████████████████████████████████████████
----------------------------------------------------------------------------------------------------------------------------------------------
 CPU1 |                                                                                                      ███████████████████████████████
----------------------------------------------------------------------------------------------------------------------------------------------
 CPU2 |                                                                                                                                 ███
------+--------------------------+--------------------------+--------------------------+--------------------------+---------------------------
  -11.00ms                    -7.00ms                    -3.00ms                    1.00ms                    5.00ms
```