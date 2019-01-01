#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import sys


def init_logger(logger_name, log_file_name):
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)-8s %(message)s",
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='%s' % (log_file_name),
                        filemode='w'
                        )
    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.NOTSET)
    return logger

