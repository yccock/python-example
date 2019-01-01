#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import threading
import time
import uuid
from urllib import request


class RequestThread(threading.Thread):
    def __init__(self, settings, ip_port_lt, server_index, in_queue_lt, out_queue_lt, logger):
        threading.Thread.__init__(self)
        self.settings = settings
        self.ip_port_lt = ip_port_lt
        self.server_index = server_index
        self.in_queue_lt = in_queue_lt
        self.out_queue_lt = out_queue_lt
        self.logger = logger

    def run(self):
        while True:
            ip_port = self.ip_port_lt[self.server_index]
            url = self.settings['url_prefix'] + ip_port + '/' + self.in_queue_lt[self.server_index].get()
            json_str = ''
            try:
                response_data = request.urlopen(url).read()
                json_data = json.loads(response_data.decode('utf-8'))
                status = json_data['status']
                info = json_data['info']
                json_str = str(status) + '\t' + info
            except Exception as err:
                self.logger.error("error(url): %s" % url)
                if hasattr(err, 'reason'):
                    self.logger.warning("ERROR:The reason is %s" % err.reason)
                elif hasattr(err, 'code'):
                    self.logger.warning("The server couldn't fulfill the request")
                    self.logger.warning("Error code:%s" % err.code)
                    self.logger.warning("Return content:%s" % err.read())
                else:  # 其他异常处理
                    self.logger.warning("misc_error: " + err.__str__())
            url_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, ip_port)
            self.in_queue_lt[self.server_index].task_done()
            self.out_queue_lt[self.server_index].put(str(url_uuid) + '\t' + json_str)
