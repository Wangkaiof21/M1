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


@safe_mode
def cmd_delete(index, file):
    """
    删除指定位置
    :param index:指定行号:为'$'时，删除最后一行.为'n,m'时，表示删除n-m行
    :param file:操作文件
    :return:
    """
    return r'sed "{}d #" {} -i'.format(index, file)


@safe_mode
def cmd_change(index, content, file):
    """
    将指定位置的值修改成content
    :param index: 指定行号:为'$'时，修改最后一行.为'n,m'时，表示将n-m行的内容用content替换
    :param content: 替换内容
    :param file: 文件
    :return:
    """
    return r"sed '{}c|{}' {} -i".format(index, content, file)


@safe_mode
def cmd_supersede(_old, _new, file, greed_mode=True, line_range=''):
    """
    将旧内容替换成新内容
    :param _old: 旧内容
    :param _new: 新内容
    :param file: 操作文件
    :param greed_mode: 贪婪模式
    :param line_range: 修改的行范围
    :return:
    """
    return r"sed -r '{}s|{}|{}|g' {} -i".format(line_range, _old, _new,
                                                file) if greed_mode else r"sed -r '{}s|{}|{}|' {} -i".format(line_range,
                                                                                                             _old, _new,
                                                                                                             file)
