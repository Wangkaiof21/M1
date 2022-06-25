#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/6/25 14:51
# @Author  : v_bkaiwang
# @File    : code_inspection.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
import ctypes
import os
import re
import sys
import time
from collections.abc import Iterable
from colorama import Fore, Style
from flake8.defaults import IGNORE

"""
需求
1.检测工程项目中不符合PEP8规范的内容
2.修改每行长度上限
3.忽略某些项目中不考量的警告信息
4.统计函数 方法代码行数 以及设定其上限

实现逻辑
1.通过安装flake8工具 并用其命令行将其调用
2.将设定每行的限制数n传入 (--max-line-length n) 拼接到命令行中
3.将需忽略的代码编号字符串ignore_code或列表 于(--extend-ignore=ignore_code或ignore_code,ignore_code1... )拼接到命令行中执行
4.a.纯函数文件无类的情况下 通过正则根据"def"确定方法首行位置且记录 如此 即可通过 下一个函数的首行位置-当前函数首行位置=当前函数代码行数
    最后一个函数代码行数 则由文件行数 - 最后一个函数首行位置 获得
  b.存在类的情况 则需相似的方法通过正则"class"获得类的范围 后再调用纯函数的方法即可统计类内的函数代码行数
    需要套注意的是 调用纯函数统计方法时 统计的起始行即为类的首行而不是默认的1
  c.以上若存在调试部分的影响 则再判断的时候增加对调试部分的处理 添加统计完后从列表中移除即可
"""

code_dict = {}
desc_dict = {}
ignore_file_list = []
CODE_TOOL = "flake8"
MAX_FUNCTION_LINES = 43
MAX_CLASS_LINES = 400
MAX_MODULE_LINES = 700
MAX_LINE_LENGTH = 120


def ignore_code(code):
    """

    :param code: 忽略代码 可以为任意可迭代数据类型或者单个忽略代码字符串
    :return:
    """
    ignore_data = set(IGNORE)
    if isinstance(code, str):
        ignore_data |= {code}
    elif isinstance(code, Iterable):
        ignore_data |= set(code)
    else:
        print(f"Unsupported type {code}")
    print("************* Ignore Items *************")
    for line in ignore_data:
        print(f"{line}:\t{desc_dict.get(line, Fore.RED + '* Wrong ignore code! ' + Style.RESET_ALL)}")
    print("************* Ignore Items *************\n")
    return ignore_data


def is_admin():
    """
    判断是否为管理员
    :return:
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        print(e)
        return False


def environment(code_tool=CODE_TOOL):
    """
    进行环境检查 缺少即执行安装 前提是python正确配置了环境变量
    :param code_tool: flake8
    :return:
    """
    env = os.popen("pip list").read()
    if code_tool not in env:
        """安装插件"""
        if is_admin():
            os.popen(f"pip install {code_tool}").read()
            print("Flake8 install Successfully!")
        else:
            if sys.version_info[0] == 3:
                print("Admin privileges are obtained and executed again")
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
                time.sleep(15)
                print("Flake8 install Successfully!")
    else:
        print("Flake8 has been existed...")


def get_data(path):
    """
    获取文件信息
    :param path:路径
    :return: 文件内容数据
    """
    with open(path, "r", encoding="utf-8") as f:
        read_data = f.read()
        return read_data

