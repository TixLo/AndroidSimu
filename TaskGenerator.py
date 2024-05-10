import random
import json
from MultiMap import MultiMap

class TaskGenerator:
    def __init__(self, task_count, cpus):
        self.task_count = task_count
        self.cpus = cpus
        self.total_cpu = len(self.cpus)

    def get_tasks(self):
        multimap = MultiMap()
        ts = []
        for i in range(self.task_count):
            ts.append(0)


        for i in range(self.task_count):
            print('ts[0]: %.6f, ts[1]:%.6f, ts[2]:%.6f' % (ts[0], ts[1], ts[2]))

            task = {}
            task['id'] = 0
            task['name'] = 'task-%d' % i
            task['pid'] = 1000 + i
            task['tgid'] = 2000
            cpu_index = random.randint(0, self.total_cpu-1)
            task['cpu'] = cpu_index
            task['ts'] = ts[cpu_index]
            if i > 0:
                task['ts'] += random.uniform(0, 0.002)
            task['dur'] = random.uniform(0.0001, 0.030)

            #instructions = 1000 MHz * 0.001ms * 1.2 IPC
            freq = self.cpus[task['cpu']]['max_freq']
            ipc = self.cpus[task['cpu']]['ipc']
            # print('freq: %d, ipc: %.2f, dur: %.6f' % (freq, ipc, task['dur']))
            task['workload'] = int(freq * 1000000 * task['dur'] * ipc)
            multimap[ts[cpu_index]] = task

            delta = random.uniform(0.010, 0.100)
            ts[cpu_index] += delta + task['dur']
            print('self.ts: %.6f, delta: %.6f, dur: %.6f' % (ts[cpu_index], delta, task['dur']))

        # sorted_dict_task = dict(sorted(multimap.items()))
        unsorted_tasks = []
        for tasks in multimap.values():
            for task in tasks:
                unsorted_tasks.append(task)

        sorted_tasks = []
        id_count = 0
        while len(unsorted_tasks) > 0:
            min_ts_task = None
            min_ts_index = -1
            for i in range(len(unsorted_tasks)):
                task = unsorted_tasks[i]
                if min_ts_index == -1:
                    min_ts_index = i
                else:
                    if task['ts'] <= unsorted_tasks[min_ts_index]['ts']:
                        min_ts_index = i

            unsorted_tasks[min_ts_index]['id'] = id_count
            id_count += 1
            sorted_tasks.append(unsorted_tasks[min_ts_index])
            del unsorted_tasks[min_ts_index]
            # print(unsorted_tasks)
            # input()

        print(json.dumps(sorted_tasks, indent=2))
        return sorted_tasks