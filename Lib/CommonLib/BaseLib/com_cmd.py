#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/15 22:17
# @Author  : v_bkaiwang
# @File    : com_cmd.py
# @Software: win10 Tensorflow1.13.1 python3.6.3

import re

from Lib.ComminLib.BaseLib.log_message import LogMessage, LOG_ERROR


def init_cmd(cmd_str, cmd_para):
    """

    :param cmd_str: “chip set a%a% [b, %b%] c %c% [%d%]”
    :param cmd_para: 使用字典传入
    :return: 拼装好可执行字符串
    """
    re_str = r'(\[?\s*\-?\w*\s*\%\s*\-?\w*\s*\%\s*\]?)'
    partten = re.compile(re_str)
    pare_list = partten.findall(cmd_str)
    # 去掉参数 只留下没有参数的命令行头
    ret_cmd = re.sub(re_str, "", cmd_str)
    # 遍历每个参数 从参数字典取值 生成替换后的命令行字符串
    for tmp_para in pare_list:
        tmp_para_str = ''
        match_obj = re.search(r'\[?\s*(\w*)\s*\%\s*\-?(\w*)\s*\%\s*\]?', tmp_para)
        if match_obj:
            para_left = match_obj.group(1)
            para_right = match_obj.group(2)
        else:
            LogMessage(level=LOG_ERROR, module='init_cmd', msg="%s 参数取值失败" % tmp_para)
            return False
        # 从参数取参数替换的值
        if cmd_para[para_right]:
            para_value = cmd_para[para_right]
            tmp_para_str = " " + para_left + " %s " % para_value
        elif not re.search(r'\[|\]', tmp_para):
            # 如果没有[则说明参数非法
            LogMessage(level=LOG_ERROR, module='init_cmd', msg="%s 参数非法 取值失败" % para_left)
            return False
        ret_cmd = ret_cmd.strip() + tmp_para_str
    return ret_cmd


def void_para(para):
    """
    检查是否是正常参数 标准None  字符串只有空格的字符串非法，返回False 长度为零的list ，dict 只提示 返回True
    :param para:
    :return:
    """
    ret = True
    if not para:
        ret = False
    elif isinstance(para, str):
        if len(para.strip()) < 1:
            ret = False
    elif isinstance(para, list) or isinstance(para, dict):
        if not para:
            LogMessage(level=LOG_ERROR, module='init_cmd', msg="%s 为空 取值失败" % para)
    else:
        pass
    return ret
