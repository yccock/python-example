#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
from queue import Queue

from PerfTest.src import SamplerMetric
from PerfTest.src.HttpLoadTest import http_load_test
from PerfTest.src.common import Constants
from PerfTest.src.thread import RequestThread, CollectorThread
from PerfTest.src.thread.ProgressRateThread import ProgressRateThread
from PerfTest.src.util import ConfigReader, LoggerHandle


class PerfTest:
    settings = {}
    ip_port_lt = []
    in_queue_lt, out_queue_lt = [], []
    urls_fname_lt, diff_fname_lt, result_fname_lt = [], [], []
    # urls_fp_lt存放请求url文件，diff_fp_lt存放响应结果文件, result_fp_lt存放统计结果文件
    urls_fp_lt, diff_fp_lt, result_fp_lt = [], []
    sampler_metric_lt = []

    def __init__(self, argv):
        # CmdLineParse.parse(argv)
        self.config_parser = ConfigReader.read("conf/setting.ini", self.settings)
        self.logger = LoggerHandle.init_logger("PerfTest", self.settings["log_path"] + self.settings["log_file"])
        self.logger.info("read ../conf/settings.ini file success")

    def start(self):
        if self.settings['single_node'] in ["True", "true", "Yes", "yes", "1"]:
            self.settings['ip_port'] = self.settings['ip_port'].strip(" \n\r\t").split(Constants.SEPARATOR)[0].strip(
                " \n\r\t")
        self.construct()
        # http load test
        http_load_threads = []
        if self.settings['stress'] in ["True", "true", "Yes", "yes", "1"]:
            http_load_threads = http_load_test(self.settings, self.result_fp_lt, self.urls_fname_lt, self.logger)
        if http_load_threads:
            for http_load_thread in http_load_threads:
                self.logger.info("start http_load_test ...")
                http_load_thread.join()
        # function test
        if self.settings['function'] in ["True", "true", "Yes", "yes", "1"]:
            self.logger.info("start function_test ...")
            self.start_request_thread()
            self.start_collector_thread()
            self.start_progress_thread()
            # wait for the task to be completed
            server_nums = self.get_server_nums()
            for index in range(server_nums):
                self.in_queue_lt[index].join()
                self.out_queue_lt[index].join()
            self.analysis_test_result()
        # close diff and result file pointer
        for diff_fp in self.diff_fp_lt:
            diff_fp.close()
        for result_fp in self.result_fp_lt:
            result_fp.close()
        if self.settings['diff'] in ["True", "true", "Yes", "yes", "1"]:
            self.diff_test()
        self.logger.info("test end!")

    def construct(self):
        server_nums = self.get_server_nums()
        self.ip_port_lt = self.settings['ip_port'].strip(" \n\r\t").split(Constants.SEPARATOR)[0:server_nums]
        # init result,diff,url,queue list
        for i in range(server_nums):
            fname_prefix = "_".join(self.ip_port_lt[i].split(':'))
            self.in_queue_lt.append(Queue())
            self.out_queue_lt.append(Queue())
            self.urls_fname_lt.append(fname_prefix + '_urls')
            self.diff_fname_lt.append(fname_prefix + '_diff')
            self.result_fname_lt.append(fname_prefix + '_res')
            # monitor list
            self.sampler_metric_lt.append(SamplerMetric.SampleMetric())
        # init queue from parameter file and write to result file
        result_path = self.settings['res_path']
        for urls_fname in self.urls_fname_lt:
            self.urls_fp_lt.append(open(result_path + urls_fname, 'w', encoding='utf-8'))
        with open(self.settings['param_path'] + self.settings['param_file'], 'r', encoding='utf-8') as fp:
            for line in fp:
                line = line.strip(" \n\r\t")
                if len(line) == 0:
                    continue
                for index, ip_port in enumerate(self.ip_port_lt):
                    self.in_queue_lt[index].put(line)
                    self.urls_fp_lt[index].write(self.settings['url_prefix'] + ip_port + '/' + line + '\n')
        for url_fp in self.urls_fp_lt:
            url_fp.close()
        # init result and diff file
        for diff_name in self.diff_fname_lt:
            self.diff_fp_lt.append(open(result_path + diff_name, 'w', encoding='utf-8'))
        for result_name in self.result_fname_lt:
            self.result_fp_lt.append(open(result_path + result_name, 'w', encoding='utf-8'))

        self.logger.info("the size of in_queue_lt[0] is: %d" % self.in_queue_lt[0].qsize())
        self.logger.info("result_files: %s" % (Constants.SEPARATOR.join(self.result_fname_lt)))
        self.logger.info("diff_files: %s" % (Constants.SEPARATOR.join(self.diff_fname_lt)))
        # self.save_setting_file()

    def save_setting_file(self):
        self.config_parser.set('TEST_RESULT', 'result_file', Constants.SEPARATOR.join(self.result_fname_lt))
        self.config_parser.set('TEST_RESULT', 'diff_file', Constants.SEPARATOR.join(self.diff_fname_lt))
        with open('conf/setting.ini', 'w+', encoding='utf-8') as fp:
            self.config_parser.write(fp)

    def get_server_nums(self):
        if self.settings['single_node'] in ["True", "true", "Yes", "yes", "1"]:
            return 1
        return len(self.settings['ip_port'].strip(" \n\r\t").split(Constants.SEPARATOR))

    def start_request_thread(self):
        self.logger.info("start request thread...")
        server_nums = self.get_server_nums()
        for server_index in range(server_nums):
            for i in self.settings['pool_size']:
                rt = RequestThread.RequestThread(self.settings, self.ip_port_lt, server_index,
                                                 self.in_queue_lt, self.out_queue_lt, self.logger)
                rt.setDaemon(True)
                rt.start()

    def start_collector_thread(self):
        self.logger.info("start collector thread...")
        server_nums = self.get_server_nums()
        for server_index in range(server_nums):
            ct = CollectorThread.CollectorThread(self.out_queue_lt[server_index], self.settings,
                                                 self.diff_fp_lt[server_index], self.sampler_metric_lt[server_index])
            ct.setDaemon(True)
            ct.start()

    def start_progress_thread(self):
        prt = ProgressRateThread(self.settings['sleep_cycle'], self.in_queue_lt, self.logger)
        prt.setDaemon(True)
        prt.start()

    def analysis_test_result(self):
        for index, result_fd in enumerate(self.result_fp_lt):
            item_res = self.sampler_metric_lt[index]
            coverage = 0
            if item_res.request_count != 0:
                coverage = float(item_res.response_count) / item_res.request_count
            result_fd.write("=======================================\n")
            result_fd.write("Some test metrics of Functional Verification are as follows\n")
            result_fd.write("\tRequest: %d\n" % item_res.request_count)
            result_fd.write("\tResponse: %d\n" % item_res.response_count)
            result_fd.write("\tCoverage: %.6f\n" % coverage)
            result_fd.write("=======================================\n")

    def diff_test(self):
        self.logger.info("start diff test...")
        for diff_fname in self.diff_fname_lt:
            diff_fname = self.settings["res_path"] + diff_fname
            if os.path.exists(diff_fname):
                cmd = "sort -nr %s -o %s" % (diff_fname, diff_fname + ".sort")
                self.logger.info('execute cmd: "%s"' % cmd)
                subprocess.call(cmd)
        self.logger.info("diff test end!!！")
