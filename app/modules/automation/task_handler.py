import heapq
import threading
import time


class TaskHandler:
    def __init__(self):
        self.task_queue = []
        self.condition = threading.Condition()
        self.exit_event = threading.Event()
        self.thread = threading.Thread(target=self._process_tasks)
        self.thread.start()

    def _process_tasks(self):
        while not self.exit_event.is_set():
            with self.condition:
                while not self.task_queue:
                    self.condition.wait()

                now = time.time()
                if self.task_queue and self.task_queue[0][0] <= now:
                    _, task = heapq.heappop(self.task_queue)
                    task()
                else:
                    next_time = self.task_queue[0][0]
                    timeout = max(0, next_time - now)
                    self.condition.wait(timeout=timeout)

    def post(self, task, delay=0):
        with self.condition:
            execute_at = time.time() + delay
            heapq.heappush(self.task_queue, (execute_at, task))
            self.condition.notify_all()

    def stop(self):
        with self.condition:
            self.exit_event.set()
            self.condition.notify_all()
