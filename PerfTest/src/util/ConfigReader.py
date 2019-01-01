#!/usr/bin/env python
# -*- coding: utf-8 -*-
import configparser


def read(setting_file, setting_dict):
    config = configparser.ConfigParser()
    config.read(setting_file)
    setting_dict['log_path'] = config['LOG']['log_path']
    setting_dict['log_file'] = config['LOG']['log_file']
    setting_dict['param_path'] = config['TEST_PARAM']['param_path']
    setting_dict['param_file'] = config['TEST_PARAM']['param_file']
    setting_dict['url_prefix'] = config['TEST_TARGET']['url_prefix']
    setting_dict['ip_port'] = config['TEST_TARGET']['ip_port']

    setting_dict['single_node'] = config['TEST_CONFIG']['single_node']
    setting_dict['pool_size'] = config['TEST_CONFIG']['pool_size']
    setting_dict['function'] = config['TEST_CONFIG']['function']
    setting_dict['stress'] = config['TEST_CONFIG']['stress']
    setting_dict['diff'] = config['TEST_CONFIG']['diff']

    setting_dict['sleep_cycle'] = config['PROGRESS_RATE']['sleep_cycle']

    setting_dict['res_path'] = config['TEST_RESULT']['res_path']
    setting_dict['result_file'] = config['TEST_RESULT']['result_file']
    setting_dict['diff_file'] = config['TEST_RESULT']['diff_file']
    return config
