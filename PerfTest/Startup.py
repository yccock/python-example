#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import signal
import sys

from PerfTest.src.PerfTest import PerfTest

# https://www.ibm.com/developerworks/cn/aix/library/au-threadingpython/index.html

def singal_handler(signum, e):
    print('==========in signum==========')
    if (signum == signal.SIGINT) or (signum == signal.SIGTERM) or (signum == signal.SIGKILL):
        exit()
    print('==========out signum=========')

if __name__ == '__main__':
    signal.signal(signal.SIGINT, singal_handler)
    signal.signal(signal.SIGTERM, singal_handler)
    # 分割当前文件的目录和文件名
    dirname, filename = os.path.split(os.path.abspath(__file__))
    # 将工作目录切换为当前文件所在的目录
    os.chdir(dirname)
    perfTest = PerfTest(sys.argv)
    perfTest.start()
