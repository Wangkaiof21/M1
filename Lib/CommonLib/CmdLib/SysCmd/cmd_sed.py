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


@safe_mode
def cmd_add(index, content, file):
    """
    指定位置后追加content
    :param index:指定行号:为'$'时，表示最后一行追加.为'n,m'时，表示在n-m行的每一行后面追加
    :param content:追加内容
    :param file:操作文件
    :return:
    """
    return r'sed {}a {} {} -i'.format(index, content, file)

