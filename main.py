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
    "cpu": 2,
    "ts": 0,
    "dur": 0.008490651573683526,
    "workload": 43472136
  },
  {
    "id": 1,
    "name": "task-3",
    "pid": 1003,
    "tgid": 2000,
    "cpu": 1,
    "ts": 0.00036701050874821497,
    "dur": 0.008033284395969382,
    "workload": 27473832
  },
  {
    "id": 2,
    "name": "task-2",
    "pid": 1002,
    "tgid": 2000,
    "cpu": 0,
    "ts": 0.00198128616206017,
    "dur": 0.008305990643019954,
    "workload": 14203243
  },
  {
    "id": 3,
    "name": "task-1",
    "pid": 1001,
    "tgid": 2000,
    "cpu": 2,
    "ts": 0.015005125060544524,
    "dur": 0.008645537743319503,
    "workload": 44265153
  },
  {
    "id": 4,
    "name": "task-6",
    "pid": 1006,
    "tgid": 2000,
    "cpu": 1,
    "ts": 0.015895463849019745,
    "dur": 0.002381816621886947,
    "workload": 8145812
  },
  {
    "id": 5,
    "name": "task-4",
    "pid": 1004,
    "tgid": 2000,
    "cpu": 0,
    "ts": 0.018329530751782865,
    "dur": 0.0049307399963093865,
    "workload": 8431565
  },
  {
    "id": 6,
    "name": "task-9",
    "pid": 1009,
    "tgid": 2000,
    "cpu": 0,
    "ts": 0.03177221110663382,
    "dur": 0.005715067610414751,
    "workload": 9772765
  },
  {
    "id": 7,
    "name": "task-5",
    "pid": 1005,
    "tgid": 2000,
    "cpu": 2,
    "ts": 0.0319140898315451,
    "dur": 0.00940888653437561,
    "workload": 48173499
  },
  {
    "id": 8,
    "name": "task-7",
    "pid": 1007,
    "tgid": 2000,
    "cpu": 2,
    "ts": 0.04722113963958774,
    "dur": 0.006008090229338324,
    "workload": 30761421
  },
  {
    "id": 9,
    "name": "task-8",
    "pid": 1008,
    "tgid": 2000,
    "cpu": 2,
    "ts": 0.05976836699881235,
    "dur": 0.007581112988308897,
    "workload": 38815298
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
            'pelt-n': 8,
            'cpu_dispatch_bypass': False,
            'idle_prefer': False,
            'task_init_util': 128,
            'load_balance': True,
            'cpu_off': [],
            'cpu_fixed_freq': [-1, -1, -1]
        }
    }
    return configs

if __name__ == '__main__':
    configs = create_hw_configs()

    task_generator = TaskGenerator(task_count=50, cpus=configs['sched']['cpus'])
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

