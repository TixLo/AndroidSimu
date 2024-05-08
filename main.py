import simpy
import json

from Android import Android
from Task import Task

tasks_data = [
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
    ,
    {
        'id': 2,
        'name': 'B',
        'pid': 112,
        'tgid': 222,
        'cpu': 1,
        'ts': 0.004000,
        'dur': 1.500000,
        'workload': 5130000 #instructions = 1000 MHz * 0.001ms * 1.2 IPC
    },
    {
        'id': 3,
        'name': 'C',
        'pid': 111,
        'tgid': 222,
        'cpu': 2,
        'ts': 0.008000,
        'dur': 1.500000,
        'workload': 5130000 #instructions = 1000 MHz * 0.001ms * 1.2 IPC
    }
]

def create_hw_configs():
    configs = {
        'android': {
            'executor_console': True 
        },
        'sched': {
            'cpus': [
                { 'max_freq': 1900, 'ipc': 0.9, 'cluster': 0},
                { 'max_freq': 2850, 'ipc': 1.2, 'cluster': 1},
                { 'max_freq': 3200, 'ipc': 1.6, 'cluster': 2}
            ],
            'pelt-n': 32,
            'cpu_dispatch_bypass': False,
            'idle_prefer': False,
            'task_init_util': 128
        }
    }
    return configs

if __name__ == '__main__':
    configs = create_hw_configs()

    # create SimPy Environment
    env = simpy.Environment()

    # create Android instance
    android = Android(env=env, name='Android', cfg=configs)

    # import tasks
    android.set_task_data(tasks_data)
    
    # booting Android system and create all necessary modules
    android.boot()

    # start executing Android system
    android.run(300) # 345ms

    android.to_trace('output.trace')

