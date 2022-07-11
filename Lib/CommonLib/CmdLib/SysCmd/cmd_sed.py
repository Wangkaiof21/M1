#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/3/4 23:38
# @Author  : v_bkaiwang
# @File    : cmd_sed.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
import time

# 安全模式flag
mode_flag = True


def safe_mode(flag):
    """
    安全模式
    :param flag:
    :return:
    """

    def decorate(func):
        def inner(*args, **kwargs):
            res = func(*args, **kwargs)
            if flag:
                cur_time = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime())
                res += '.{}'.format(cur_time)
            return res

        return inner

    return decorate
