#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from distutils import command


def http_load_test(settings, result_fp_lt, urls_fname_lt, logger):
    logger.info("begin to http_load test...")
    parameters = settings["parameters"]
    http_load_threads = []
    for num in range(len(urls_fname_lt)):
        urls_fname = settings["fpath"] + urls_fname_lt[num]
        cmd = "http_load %s %s" % (parameters, urls_fname)
        th = threading.Thread(target=exec_cmd, args=(result_fp_lt, num, cmd, logger))
        http_load_threads.append(th)
        th.start()
    return http_load_threads


def exec_cmd(result_fp_lt, num, cmd, logger):
    try:
        logger.info('cmd "%s" start executing...' % cmd)
        result_fp_lt[num].write('cmd "%s" start executing...\n' % cmd)
        (status, output) = command.getstatusoutput(cmd)
        result_fp_lt[num].write("=======================================\n")
        result_fp_lt[num].write("Some test metrics of HTTP_LOAD are as follows\n")
        result_fp_lt[num].write("status: %d\n" % status)
        result_fp_lt[num].write(output)
        result_fp_lt[num].write("\n=======================================\n")
        logger.info('cmd "%s" execute end!!!' % cmd)
    except Exception as e:
        logger.warning('"%s"\t execute failed, the reason is: %s' % (cmd, e))
        result_fp_lt[num].write('"%s"\t execute failed, the reason is: %s\n' % (cmd, e))
