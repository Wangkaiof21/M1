#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/4 12:39
# @Author  : v_bkaiwang
# @File    : log_message.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
# 日志打印函数 全局使用
__author__ = "Zhanyi.zsm, 247473"
__copyringht__ = "Copyright AIS, Alibaba"

import logging
import os
import sys
import time
from functools import wraps
from colorama import Fore, Style

TIMER_FLAG = False

# 定义日志打印等级
LOG_DEBUG = logging.DEBUG
LOG_INFO = logging.INFO
LOG_WARN = logging.WARN
LOG_ERROR = logging.ERROR
# 用于测试框架的打印级别 特殊定义为90
LOG_SYS = 90
logging.addLevelName(LOG_SYS, "SYS ")
_LEVEL_COLOR = {
    LOG_DEBUG: Fore.BLUE,
    LOG_INFO: Fore.WHITE,
    LOG_WARN: Fore.YELLOW,
    LOG_ERROR: Fore.RED,
    LOG_SYS: Fore.GREEN
}


def LogMessage(level=LOG_INFO, module="NA", msg="NA", logger_name="iAutos"):
    """

    :param level: logger级别
    :param model: logger模块前缀
    :param msg: logging信息
    :param logger_name: 全局可注册多个不同名logger
    :return:
    """
    logger = logging.getLogger(logger_name)
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    caller = ""
    if level == LOG_ERROR or level == LOG_WARN:
        # 获取调用者的函数名
        f_back = sys._getframe().f_back
        co_name = f_back.f_code.co_name
        file_name = os.path.basename(f_back.f_code.co_filename)
        line_no = f_back.f_lineno
        caller = f"\t[{file_name}:{line_no}-{co_name}]"
    level_name = logging.getLevelName(level)
    color = _LEVEL_COLOR.get(level)
    log_msg = "\n".join(
        [f'{color}{t}\t{level_name}\t[{module}]\t{row}{caller}{Style.RESET_ALL}' for row in str(msg).split("\n")])
    logging.log(level, log_msg)


def func_name_wrapper(func):
    """
    在函数被装饰函数调用时 打印名称

    :param func:
    :return:
    """

    @wraps(func)
    def inner(*args, **kwargs):
        logger = logging.getLogger("iAutos")
        logging.info(Fore.GREEN + f"Call {func.__name__}..." + Style.RESET_ALL)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(Fore.RED + f"{e}" + Style.RESET_ALL)
            pass

    return inner


def timer(flag=TIMER_FLAG):
    """
    计算被装饰函数执行时间
    :param flag: 为ture时统计每个被执行函数时间
    :return:
    """

    def outer(fn):
        def inner(*args, **kwargs):
            if flag:
                # time.perf_counter()是个计数器 第一次调用是0
                start_time = time.perf_counter()
                res = fn(*args, **kwargs)
                end_time = time.perf_counter()
                print(f"⬤ {fn.__name__} spend {end_time - start_time} seconds")
            else:
                res = fn(*args, **kwargs)
            return res

        return inner

    return outer
