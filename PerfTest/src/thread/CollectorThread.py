#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading

class CollectorThread(threading.Thread):
    def __init__(self, out_queue, settings, diff_fp, sampler_metric):
        threading.Thread.__init__(self)
        self.out_queue = out_queue
        self.settings = settings
        self.diff_fp = diff_fp
        self.sampler_metric = sampler_metric

    def run(self):
        while True:
            write_file_flag = True if (self.settings["diff"] in ["True", "true", "Yes", "yes", "1"]) else False
            data = self.out_queue.get()
            if write_file_flag:
                self.diff_fp.write(data + '\n')
            content = data.strip(" \t\r\n").split("\t")
            if len(content) > 0:
                self.sampler_metric.request_count += 1
                self.sampler_metric.response_count += 1
            self.out_queue.task_done()
