import numpy as np
import logging


class Progress:
    def __init__(self, total, min_elapsed_sec=10):
        self.start = np.datetime64('now')
        self.last_report_time = self.start
        self.current = 0
        self.total = total
        self.logger = logging.getLogger(str(__name__).split('.')[0])
        self.min_elapsed = np.timedelta64(min_elapsed_sec, 's')

    def update(self, current):
        self.current = current
        elapsed = np.datetime64('now') - self.last_report_time
        if elapsed >= self.min_elapsed:
            self.report()

    def report(self):
        self.last_report_time = np.datetime64('now')
        one_sec = np.timedelta64(1, 's')
        sec_elapsed = (self.last_report_time - self.start) / one_sec
        num_finished = self.current + 1
        sec_per_item = sec_elapsed / num_finished
        sec_remaining = (self.total - num_finished) * sec_per_item
        time_remaining = np.timedelta64(int(1e6 * sec_remaining), 'us')
        estimated_finish_time = self.last_report_time + time_remaining
        eta_str = estimated_finish_time.astype('datetime64[s]').astype(str)
        eta_str = str(eta_str).replace('T', ' ')
        self.logger.info(f'Progress: {num_finished} / {self.total}  (ETA: {eta_str})')
