import time
import re


class Stopwatch:
    __format_pattern = re.compile(r'{(.*?)}')

    def __init__(self, display_format: str = ''):
        self.display_format = display_format
        self.start_time = 0.0
        self.total_time = 0.0

    def start(self):
        self.start_time = time.time()

    def reset(self):
        self.start_time = 0.0
        self.total_time = 0.0

    def stop(self):
        time_difference = time.time() - self.start_time
        self.total_time = round(time_difference, 3 if time_difference >= 0.1 else 5)

    def display_time(self):
        format_args = re.findall(self.__class__.__format_pattern, self.display_format)
        self.stop()
        if len(format_args) != 0:
            print(self.display_format.format(self.total_time))
        else:
            print(self.total_time)

    @classmethod
    def start_new(cls, display_format: str = '') -> "Stopwatch":
        instance = Stopwatch(display_format)
        instance.start()
        return instance
