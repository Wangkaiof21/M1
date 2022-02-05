#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/4 22:26
# @Author  : v_bkaiwang
# @File    : ExcelRealFunc.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
# Excel 原生读取
import os
from openpyxl import load_workbook
import time
import sys
import csv

PID = sys.argv[1]


def read_excel_body(file_name):
    """
    读取xlsx的表格信息 组成列表返回
    :param file_name:
    :return:
    """
    wb1 = load_workbook(file_name)
    sheet = wb1['description']
    sheet2 = wb1['variable']

    title_range = sheet['A5':'H5']
    data_bus = sheet['D2']
    title = list()
    for titles in title_range:
        for name in titles:
            title.append(name.value)

    row_index = 2
    col_index = 1
    max_col_index = 2
    variable_list = list()
    while True:
        row_list = list()
        while col_index <= max_col_index:
            value = sheet2.cell(row_index, col_index).value
            row_list.append(value)
            col_index += 1
        row_index += 1
        col_index = 1
        if all(i is None for i in row_list):
            break
        variable_list.append(row_list)

    # body数据 不停的往下读取数据 撞到全是空的就中断
    row_index = 6
    col_index = 1
    max_col_index = 8
    body_list = list()
    while True:
        row_list = list()
        while col_index <= max_col_index:
            value = sheet.cell(row_index, col_index).value
            row_list.append(value)
            col_index += 1
        row_index += 1
        col_index = 1
        if all(i is None for i in row_list):
            break
        body_list.append(row_list)

    # 分组 撞到空行就下一组
    list_bodys = list()
    list_body = list()
    for line in body_list:
        if line[0] is not None:
            list_bodys.append(list_body)
            list_body = []
        list_body.append(line)
    list_bodys.append(list_body)
    list_bodys.pop(0)


# 读取文件与写入
def read_file_and_write():
    """
    读取固定文件 获取特殊行 去掉0占用 去掉重复数据
    :return:
    """
    # 当前文件夹
    file_path = os.path.dirname(os.path.abspath(__file__))
    SYS_TIME = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    FILE_NAME = f'Core_function_{PID}_{SYS_TIME}'
    file = file_path + '/' + FILE_NAME + '.csv'
    with open(file, 'r', encoding='utf-8')as f:
        reader = list(csv.reader(f))
    reader = list(filter(None, reader))
    # 获取特殊行
    hot_point = list()
    for line in reader:
        if '#' not in line[0] and '%' in line[0]:
            line = ''.join(line)
            new_line = line.strip().split()
            hot_point.append(new_line)
    # 去除0.00% 占用数
    format_list = list()
    for point in hot_point:
        if point[1] != '0.00%' and point not in format_list:
            format_list.append(point)
    format_list.sort(key=take_second, reverse=True)
    top_num = len(format_list)
    if top_num > 3:
        format_list = format_list[:3]
    else:
        format_list = format_list
    csv_name = f'{FILE_NAME}_TOP3.csv'
    # python2 有new_line=''参数 python3则没有 需要手动添加'\n'
    with open(csv_name, 'w') as w:
        writer = csv.writer(w)
        for i in format_list:
            writer.writerrow(i)
            writer.writerrow('\n')


def take_second(elem):
    return elem[1]


