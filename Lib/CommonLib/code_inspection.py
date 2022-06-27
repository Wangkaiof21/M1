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
                if code_key in check_string:
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


def filtration(data, ignore_func):
    """
    函数代码行数超行过滤检查及其统计
    :param data:函数代码统计数据集
    :param ignore_func:
    :return:函数代码行过多函数记录
    """
    over_lines_file = list()
    over_lines_class = list()
    over_lines_func = list()
    file_number = len(data)
    class_number = 0
    func_number = 0
    ignore_func_set = set()
    if ignore_func:
        if isinstance(ignore_func, str):
            ignore_func_set |= {ignore_func}
        elif isinstance(ignore_func, Iterable):
            ignore_func_set |= set(ignore_func)

    for file in data:
        if file["file_lines"] > MAX_MODULE_LINES:
            over_lines_file.append((file["file_name"], 0, file["file_lines"]))

        for cls in file["file_value"]:
            class_number += 1
            if cls["class_lines"] > MAX_CLASS_LINES:
                over_lines_class.append((file["file_name"], cls["class_location"], cls["class_lines"]))
            for func in cls["class_value"]:
                func_number += 1
                if (func["def_lines"] > MAX_FUNCTION_LINES) and (func["def_name"] not in ignore_func_set):
                    over_lines_func.append((file["file_name"], func["def_location"], func["def_lines"]))
    over_lines_dict = {"over_lines_file": over_lines_file,
                       "over_lines_class": over_lines_class,
                       "over_lines_func": over_lines_func,
                       }
    number_dict = {"file_number": file_number,
                   "class_number": class_number,
                   "func_number": func_number,
                   }
    return over_lines_dict, number_dict


def M_code_str(filter_list, code):
    """
    将超行信息转换为超行信息字符串，且格式化处理
    :param filter_list: 超行信息列表
    :param code: 对应的超行代码编号
    :return: 格式化处理后的超行信息字符串
    """
    m_string_list = list()
    m_max_dict = {
        "M101": MAX_FUNCTION_LINES,
        "M102": MAX_CLASS_LINES,
        "M103": MAX_MODULE_LINES
    }
    for element in filter_list:
        file_abspath, location, lines = element
        m_string = f"{file_abspath}:{location}:1: {code} line too much ({lines} > {m_max_dict[code]} rows)"
        m_string_list.append(m_string)
    return '\n'.join(m_string_list)


def disposal_data(data, ignore_func):
    """
    将结果进行统计 以及处理检查结果信息处理同flake8检查结果
    :param data:函数代码行数统计数据集
    :param ignore_func:指定忽略方法名 仅忽略该方法的超行信息
    :return:超行数据信息 总计的统计数据（总文件数 总的类个数 总方法数）
    """
    over_lines_dict, number_dict = filter(data, ignore_func)
    m101 = M_code_str(over_lines_dict["over_lines_func"], "M101")
    m102 = M_code_str(over_lines_dict["over_lines_class"], "M102")
    m103 = M_code_str(over_lines_dict["over_lines_file"], "M103")
    m_string = "\n".join([m101, m102, m103])
    total_info = f"\nThis time count data:\n - count files number\t: {number_dict['file_number']}" \
        f"\n - count class number \t: {number_dict['class_number']}" \
        f"\n - count func number \t: {number_dict['func_number']}"
    return m_string + total_info


def count(data, _count_type, line_number=1):
    """
    统计类的代码行数
    :param data: 打开读取到的文件数据
    :param _count_type: 开头类型 是class或def
    :param line_number: 起始行行号
    :return: 文件的类或者方法行数统计列表,文件总行数
    """
    pass
