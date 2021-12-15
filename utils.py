import psutil
import time


class MemoryChecker:
    def __init__(self, threshold: float, call_control: int = 100):
        """
        Checks if memory has reached a certain threshold.
        Calls to the has_reached_threshold only truly check memory used
        every so often which results in false being returned in almost all of the calls.
        This behavior can be controlled by the 'call_control' parameter.
        :param threshold: Memory Threshold
        :param call_control: Number of times that the has_reached_threshold needs
        to be called before a memory check is performed.
        """
        self._self_process = psutil.Process()
        self.threshold = threshold
        self.call_control = call_control
        self._call_count = 0

    def has_reached_threshold(self):
        self._call_count += 1
        if self._call_count % self.call_control == 0:
            return self._check_memory()

        return False

    def _check_memory(self):
        used_memory = self._self_process.memory_info().vms
        total_memory = psutil.virtual_memory().total

        return (used_memory / total_memory) > self.threshold


def format_time_interval(time_stamp):
    return time.strftime('%H:%M:%S', time.gmtime(time_stamp))
