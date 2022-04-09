#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/3/4 21:19
# @Author  : v_bkaiwang
# @File    : msg_center.py
# @Software: win10 Tensorflow1.13.1 python3.6.3

import os
import time
import logging
import logging.handlers

# 每个日志大小100m
# LOG_MAX_SIZE = 100
#
#
# class MsgCenter(object):
#     def __init__(self, testcase_name=None):
#         self.case_name = testcase_name
#         self.file_hander = None
#         self.console_header = None
#         # step1 创建一个log
#         self.logger = logging.getLogger('iAutos')
#         self.logger.handlers.clear()
#         self.logger.setLevel(logging.INFO)
#         # 时间格式
#         date_time = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
#         # 默认当前目录为根目录
#         log_path = os.getcwd()
#         log_path = os.path.join(log_path, 'TestLog')
#         if not os.path.exists(log_path):
#             os.mkdir(log_path)
#         log_name = date_time + '-' + self.case_name + '.log'
#         log_name = os.path.join(log_path, log_name)
#
#         self.file_hander = logging.FileHandler(log_name, mode='w+', encoding='utf-8')
#
#         self.file_hander.setLevel(logging.INFO)  # 输出到file的log等级开关
#         # step2 创建2个handlers 用于写入日志和打印到控制台
#         self.console_header = logging.StreamHandler()
#         self.console_header.setLevel(logging.INFO)
#         # step3 定义header输出格式
#         logging.datefmt = '%Y-%m-%d %H:%M%:%S'
#         formatter = logging.Formatter("%(asctime)s -%(levelname)s %(message)s")
#         self.file_hander.setFormatter(formatter)
#         self.console_header.setFormatter(formatter)
#         # step4 将hander添加到logger里
#         self.logger.addHandler(self.file_hander)
#         self.logger.addHandler(self.console_header)

# 每个日志大小100m
LOG_MAX_SIZE = 100 * 1024 * 1024
_DEFAULT_LOG_LEVEL = logging.INFO


class MsgCenter(object):
    def __init__(self, testcase_name=None, logger_name='iAutos', level=_DEFAULT_LOG_LEVEL):
        self.case_name = testcase_name
        self.file_hander = None
        self.console_header = None
        # 第一步 创建一个logger
        self.logger = logging.getLogger(logger_name)
        self.logger.handlers.clear()
        self.logger.setLevel(level)  # log 等级总开关

        # 第二部 创建两个hander 用于写入日志文件和打印到控制台
        date_time = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())

        # 默认当前目录为根目录
        log_path = os.getcwd()
        log_path = os.path.join(log_path, "Test_log")
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        log_name = date_time + "_" + self.case_name + ".log"
        log_name = os.path.join(log_path, log_name)

        self.file_hander = logging.FileHandler(log_name, mode="w+", encoding='utf-8')
        self.file_hander.setLevel(level)
        # STEP2 01
        self.console_header = logging.StreamHandler()
        self.console_header.setLevel(level)
        self.logger.addHandler(self.file_hander)
        self.logger.addHandler(self.console_header)

    def log_level_set(self, level=logging.INFO):
        self.file_hander.setLevel(level)
        self.console_header.setLevel(level)


if __name__ == '__main__':
    msg = MsgCenter(testcase_name='testcase_001')
    msg.logger.debug('this is a logger debug message')
    msg.logger.info('this is a logger info message')
    msg.logger.warning('this is a logger warning message')
    msg.logger.error('this is a logger error message')
    msg.logger.critical('this is a logger critical message')
