#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/15 10:53
# @Author  : v_bkaiwang
# @File    : cmd_template.py 命令行返回值解析
# @Software: win10 Tensorflow1.13.1 python3.6.3

# 消息模板支持类型
from Lib.ComminLib.BaseLib.log_message import LogMessage, LOG_INFO, LOG_ERROR

NormalTxt = 'NormalTxt'
NormalTable = 'NormalTxt'


def str_get(txt_str, var_map=None, split_char=':'):
    """
    适用于解析NormalTxt类消息
    参考格式：
    chip count get
    total pkt 10000
    total bytes :0000
    :param txt_str:要解析的字符串
    :param var_map:用户指定的字符串映射{"key": "value"}
    :param split_char:
    :return:列表[{"total pkt": "10000", "total bytes": "0000"}]
            为了返回一致处理 此处返回的是只有一个元素的列表
    """
    if not var_map:
        var_map = dict()
    ret_dict = dict()
    last_key = None
    for line in txt_str.split("\n"):
        key_value = line.split(split_char)
        if len(key_value) == 2:
            # 按分号split 左边做key 右边做value
            dict_key = key_value[0].strip()
            dict_value = key_value[1].strip()
            ret_dict[dict_key] = dict_value
            last_key = dict_key

        elif len(key_value) == 1:
            # 此情况为上一行value太长 以至于打印到下一行 此时 value追加到上一行value中
            last_value = ret_dict.pop(last_key)  # ? 应该用del
            last_value += key_value[0].strip()
            ret_dict[last_key] = last_value

    if var_map:
        # 注意此处的ret_dict的copy 我们要修改ret_dict
        ret_dict_copy = ret_dict.copy()
        for dict_key, dict_value in ret_dict_copy.items():
            if dict_key in var_map:
                new_key = var_map[dict_key]
                ret_dict[new_key] = dict_value
    ret = [ret_dict]
    return ret


def table_get(table_str, var_map, split_char='|'):
    """
    table_str:
    nic | total pkt | total byte | error pkt
     0 | 1000000000 |    5000    |    100
     1 | 1000000000 |    3000    |    100
     2 | 1000000000 |    99000   |    100
    :param table_str:
    :param var_map:用户指定的字符串映射{"key": "value"}
    :param split_char:
    :return:列表[{"total pkt": "10000", "total bytes": "0000"}]
            为了返回一致处理 此处返回的是只有一个元素的列表
    """
    ret_dict_list = []
    str_list = table_str.split("\n")
    row_count = len(str_list)
    if row_count > 1:
        title_list = str_list[0].split(split_char)
        for row in range(1, row_count):
            value_list = str_list[row].split(split_char)
            # 检查异常 表头个数是否与数据个数相等
            if len(title_list) != len(value_list):
                LogMessage(level=LOG_ERROR, module='table_get', msg=f"{table_str}:表头个数不相等")
                return False

            # 核心语句 将表头分别和每行数据合成一个dict 添加到list中
            ret_dict_list.append(dict(zip(title_list, value_list)))
    else:
        LogMessage(level=LOG_ERROR, module='table_get', msg=f"{table_str}:数据异常 / 无数据警告")
        return ret_dict_list
