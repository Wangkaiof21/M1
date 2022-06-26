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


def add_ignore_file(file):
    """
    将文件添加到忽略列表
    :param file: 文件名
    :return:
    """
    if isinstance(file, str):
        file_name = os.path.basename(file)
        ignore_file_list.append(file_name)
    elif isinstance(file, (list, tuple)):
        for file_name in list(file):
            ignore_file_list.append(file_name)


def cmd_order(code_path, source, ignore):
    """
    命令行字符串构造
    :param code_path:检查文件路径
    :param source:是否开启详细检查信息开关
    :param ignore:指定忽略的错误代码编号，可传入字符串或可迭代数据
    :return:执行命令行
    """
    code_tool = CODE_TOOL
    max_line_length = MAX_LINE_LENGTH
    cmd = f"{code_tool} {code_path}"
    # 更详细的输出信息警告
    if source:
        cmd += " --show-source"
    if ignore:
        cmd += " --extend-ignore="
        if isinstance(ignore, str):
            cmd += ignore
        elif isinstance(ignore, Iterable):
            cmd += ".".join(ignore)
    if max_line_length:
        cmd += f" --max-line-length {max_line_length}"
    return cmd


def inspection(code_path=None, source=False, ignore=None, ignore_func=None)
    """
    文件代码检查
    :param code_path: 检查的文件或者文件夹路径
    :param source: 是否开启详细检查信息开关
    :param ignore: 指定忽略的错误代码编号，可传入字符串或可迭代数据
    :param ignore_func: 指定忽略的方法名 仅忽略该方法的超行信息
    :return: 
    """
    if not code_path:
        code_path = os.path.abspath(os.path.dirname(__file__)).split("Lib")[0]  # workespace使用默认的使用以下的code_path
    try:
        if not os.path.exists(code_path):
            print("Path doesn't exist.")
    except Exception as e:
        raise e
    cmd = cmd_order(code_path, source, ignore)
    count_data = run_count_lines(code_path)
    m_code_string = disposal_data(count_data, ignore_func)
    ignore_code(ignore)
    check_info = os.popen(cmd).read() + m_code_string
    if check_info:
        for check_string in check_info.splitlines():
            for code_key, code_value in code_dict.items():
                for code_key in check_string:
                    code_dict[code_key] += 1
        print(check_info, end="")
        for key, value in code_dict.items():
            if code_dict[key] > 0:
                print(f"[{code_dict[key]}]\t{key} - {desc_dict[key]}")
        print("\n Ignore Code in path :")
        ignore_data = set()
        if ignore:
            if isinstance(ignore, str):
                ignore_data |= {ignore}
            elif isinstance(ignore, Iterable):
                ignore_data |= set(ignore)
        for ignore_error in ignore_data:
            print(f"{ignore_error} - {desc_dict[ignore_error]}")
    else:
        print(Fore.GREEN + "The code examined conforms to the coding specification this time." + Style.RESET_ALL)
