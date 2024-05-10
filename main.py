import simpy
import json

from Android import Android
from Task import Task
from TaskGenerator import TaskGenerator

tasks_data = \
[
  {
    "id": 0,
    "name": "task-0",
    "pid": 1000,
    "tgid": 2000,
    "cpu": 0,
    "ts": 0,
    "dur": 0.21582861532513994,
    "workload": 369066932
  },
  {
    "id": 1,
    "name": "task-1",
    "pid": 1001,
    "tgid": 2000,
    "cpu": 1,
    "ts": 0.0017455115237506146,
    "dur": 0.024983924144307126,
    "workload": 85445020
  },
  {
    "id": 2,
    "name": "task-2",
    "pid": 1002,
    "tgid": 2000,
    "cpu": 0,
    "ts": 0.21859420196490506,
    "dur": 0.4733653019029423,
    "workload": 809454666
  },
  {
    "id": 3,
    "name": "task-3",
    "pid": 1003,
    "tgid": 2000,
    "cpu": 0,
    "ts": 0.694786781803787,
    "dur": 0.001389146851534451,
    "workload": 2375441
  },
  {
    "id": 4,
    "name": "task-4",
    "pid": 1004,
    "tgid": 2000,
    "cpu": 1,
    "ts": 0.026925885742297106,
    "dur": 0.24250420257302258,
    "workload": 829364372
  },
  {
    "id": 5,
    "name": "task-5",
    "pid": 1005,
    "tgid": 2000,
    "cpu": 1,
    "ts": 0.2724612237747409,
    "dur": 0.47479328795802,
    "workload": 1623793044
  }
]

def create_hw_configs():
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
            'pelt-n': 32,
            'cpu_dispatch_bypass': True,
            'idle_prefer': False,
            'task_init_util': 128,
            'cpu_off': [],
            'cpu_fixed_freq': [-1, -1, -1]
        }
    }
    return configs

if __name__ == '__main__':
    configs = create_hw_configs()

    task_generator = TaskGenerator(task_count=10, cpus=configs['sched']['cpus'])
    tasks_data = task_generator.get_tasks()
    # input()

    # create SimPy Environment
    env = simpy.Environment()

    # create Android instance
    android = Android(env=env, name='Android', cfg=configs)

    # import tasks
    android.set_task_data(tasks_data)
    
    # booting Android system and create all necessary modules
    android.boot()

    # start executing Android system
    android.run(-1) # 345ms

    android.to_trace('output.trace')

