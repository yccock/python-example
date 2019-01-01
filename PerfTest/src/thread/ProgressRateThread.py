#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import time


class ProgressRateThread(threading.Thread):
    """用于打印进度信息"""

    def __init__(self, sleep_cycle, in_queue_lt, logger):
        threading.Thread.__init__(self)
        self.sleep_cycle = sleep_cycle
        self.in_queue_lt = in_queue_lt
        self.logger = logger

    def run(self):
        while True:
            for index, in_queue in enumerate(self.in_queue_lt):
                self.logger.info(">>>>>> remained urls for in_queue[%d]: %d <<<<<<" % (index, in_queue.qsize()))
            time.sleep(int(self.sleep_cycle))
