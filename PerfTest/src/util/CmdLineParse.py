#!/usr/bin/env python
# -*- coding: utf-8 -*-
import getopt

import sys


def usage(name):
    print("Usage:", name, "-c <config_file> -s <source_file>")


def parse(argv):
    config_file, source_file = "",""
    try:
        opts, args = getopt.getopt(argv[1:], "hc:s:", ["help", "config", "source"])
    except getopt.GetoptError:
        usage(argv[0])
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(argv[0])
            sys.exit(1)
        elif opt in ("-c", "--config"):
            config_file = arg
        elif opt in ("-s", "--source"):
            source_file = arg
        else:
            usage(argv[0])
            sys.exit(1)
    if config_file == "" or source_file == "":
        usage(argv[0])
        sys.exit(1)
    return config_file, source_file