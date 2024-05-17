import sys
import os
import time
import termios
import tty

from UI.Point import Point
from HW.CPU import CPU
from Task import Task

class Console:
    def __init__(self):
        self.width, self.height = self.get_console_size()
        self.cursor = Point(1, 1)
        self.drawing_cpu_start_pos = 6
        self.stdout_original_settings = termios.tcgetattr(sys.stdin)

        self.init_color()

        # update information
        self.curr_time = 0
        self.delta_time = 0
        self.input_task_count = 0
        self.tick_evts = {}
        self.cpus = []
        self.showing_period = 20 #10ms
        self.showing_offset_ts = 4 #ms

    def init_color(self):
        self.RED = '\033[91m'
        self.GREEN = '\033[92m'
        self.YELLOW = '\033[93m'
        self.BLUE = '\033[94m'
        self.MAGENTA = '\033[95m'
        self.CYAN = '\033[96m'
        self.WHITE = '\033[97m'
        self.RESET = '\033[0m'

    def get_key(self):
        tty.setcbreak(sys.stdin.fileno())
        key = ord(sys.stdin.read(1))
        return key


    def get_console_size(self):
        try:
            size = os.get_terminal_size(0)  # 0 for current terminal
            return size.columns, size.lines
        except OSError:  # Handles cases where the terminal size cannot be determined
            return None

    def finalized(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.stdout_original_settings)

    def clear(self):
        os.system('clear')
        self.cursor = Point(1, 1)
        self.move()

    def move(self):
        self.move_to(self.cursor.x, self.cursor.y)

    def move_to(self, x, y):
        sys.stdout.write(f"\033[{y};{x}H")  # Move cursor to position (x, y)
        sys.stdout.flush()

    def move_to_next_new_line(self):
        self.cursor += Point(0, 1)
        self.move()

    def draw_text(self, text, color):
        print(color + text + self.RESET)

    def draw_h_line(self, color):
        print(color + '-' * self.width + self.RESET)

    def draw_system_status(self):
        info = 'Current Time: %s%.2f ms%s' % (self.YELLOW, self.curr_time, self.RESET)
        info += ', Walk Time: %s%.2f ms%s' % (self.YELLOW, self.delta_time, self.RESET)

        completed_count = 0
        for c in self.cpus:
            completed_count += len(c.completed_tasks)
        remaining_count = self.input_task_count - completed_count

        info += ', Remaining Task Count: %s%d%s' % (self.YELLOW, remaining_count, self.RESET)
        self.draw_text(info, self.RESET)
        self.move_to_next_new_line()

        self.draw_h_line(self.WHITE)
        self.move_to_next_new_line()

    def draw_cpus_info(self):
        for i in range(len(self.cpus)):
            c = self.cpus[i]
            if c.off == False:
                info = 'CPU%d' % c.index
            else:
                info = '[%sOFF%s]CPU%d' % (self.RED, self.RESET, c.index)

            info += ', util: %s%d%s' % (self.YELLOW, c.util, self.RESET)
            if c.task != None:
                info += ', task: %s%s%s' % (self.YELLOW, c.task.name, self.RESET)
                info += ', workload: %s%d%s' % (self.YELLOW, c.task.rt_workload, self.RESET)
                info += ', consumed: %s%d%s' % (self.YELLOW, c.consumed_workload, self.RESET)
            else:
                info += ', task: None, workload: -, consumed: -'
            info += ', Util: %s%d%s' % (self.YELLOW, c.util, self.RESET)
            info += ', freq: %s%d%s MHz' % (self.YELLOW, c.freq, self.RESET)
            info += ', Q: %s%d%s' % (self.YELLOW, len(c.runnable), self.RESET)
            info += ', Done: %s%d%s' % (self.YELLOW, len(c.completed_tasks), self.RESET)

            self.draw_text(info, self.WHITE)
            self.move_to_next_new_line()

    def draw_cpus_tasks(self):
        start_ts = self.curr_time - self.showing_period
        end_ts = self.curr_time

        start_pos = self.drawing_cpu_start_pos
        end_pos = self.width

        #
        #draw event label
        #
        evt_y_pos = self.cursor.y
        self.move_to_next_new_line()

        out_of_date_evts = []
        for e in self.tick_evts:
            if self.tick_evts[e] <= start_ts:
                out_of_date_evts.append(e)
        for e in out_of_date_evts:
            del self.tick_evts[e]
        for e in self.tick_evts:
            pos = int(((self.tick_evts[e] - start_ts) / self.showing_period) * (self.width - start_pos)) - 8 + start_pos
            self.move_to(pos, evt_y_pos)
            print(e)

        evt_y_pos = self.cursor.y
        self.move_to_next_new_line()
        for e in self.tick_evts:
            pos = int(((self.tick_evts[e] - start_ts) / self.showing_period) * (self.width - start_pos))
            self.move_to(pos, evt_y_pos)
            print('v')
        self.draw_h_line(self.WHITE)
        self.move_to_next_new_line()

        #
        #draw cpu and tasks
        #
        for i in range(len(self.cpus)):
            c = self.cpus[i]
            self.draw_text(' CPU%d |' % c.index, self.WHITE)
            self.draw_cpu_tasks(c)
            #draw tasks
            self.move_to_next_new_line()

            if i < len(self.cpus) - 1:
                self.draw_h_line(self.WHITE)
                self.move_to_next_new_line()

        #
        #draw the timeline
        #
        offset_num = int((end_ts - start_ts) / self.showing_offset_ts)
        offset_pos = int((end_pos - start_pos) / offset_num) - 1
        timeline = '-' * start_pos
        timeline_count = start_pos

        timeline_label = '  %.2fms' % start_ts
        for i in range(offset_num):
            if i == offset_num - 1:
                timeline += '+' + '-' * (self.width - timeline_count - 1)
            else:
                timeline += '+' + '-' * offset_pos
                timeline_count += (offset_pos + 1)
                timeline_label += ' ' * (offset_pos - 6) + '%.2fms' % (start_ts + self.showing_offset_ts * (i + 1))
        print(timeline)
        self.move_to_next_new_line()
        print(timeline_label)
        self.move_to_next_new_line()
        
    def draw_paused(self):
        self.move_to(1, self.height - 1)
        self.draw_text('Press any key to continue or Ctrl-C to exit...', self.WHITE)

    def draw_cpu_tasks(self, cpu):
        start_ts = self.curr_time - self.showing_period
        end_ts = self.curr_time
        task_drawing_max_width = self.width - self.drawing_cpu_start_pos

        drawing_tasks = []
        if cpu.task != None:
            drawing_tasks.append(cpu.task)
        
        for task in cpu.completed_tasks:
            if task.rt_e_ts > start_ts:
                drawing_tasks.append(task)
            else:
                break

        for t in drawing_tasks:
            task_start_pos = 0
            task_end_pos = 0
            task_color = self.WHITE

            task_b_t = t.rt_b_ts * 1000
            task_e_t = t.rt_e_ts * 1000

            if task_b_t >= start_ts:
                task_start_pos = task_drawing_max_width * ((task_b_t - start_ts)/self.showing_period) + self.drawing_cpu_start_pos + 2
            else:
                task_start_pos = self.drawing_cpu_start_pos + 2

            if task_e_t < 0:
                task_end_pos = self.width - 1
                task_color = self.BLUE
            elif task_e_t < end_ts:
                task_end_pos = task_drawing_max_width * ((task_e_t - start_ts)/self.showing_period) + self.drawing_cpu_start_pos
            else:
                task_end_pos = self.width - 1

            if int(task_end_pos - task_start_pos) == 0:
                task_end_pos += 2
            self.move_to(int(task_start_pos), self.cursor.y)
            bar = '█' * int(task_end_pos - task_start_pos)
            self.draw_text(bar, task_color)


    def update(self):
        self.clear()

        self.draw_system_status()

        self.draw_cpus_info()

        self.draw_cpus_tasks()

        self.draw_paused()

        # self.get_key()
        time.sleep(0.2)

