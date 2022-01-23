#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/17 17:43
# @Author  : v_bkaiwang
# @File    : excel.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
"""

Excel
sheet_exist 装饰器 在涉及表操作之前 先检查表是否存在 没有则创建
save_excel 保存 另存为
sheet_handler 获取表对象如果表名不在excel里就创建
sheet_delete 删除表
cell_handler 获取单元格对象
query 从Excel查询指定范围的数据
row_insert 在指定的行之上插入若干行
row_delete 删除行
rows_delete_discrete 删除不连续的多行
columns_name_get 将sheet的第一行作为列名 显示所有列的名称和对应的列数
column_index_get_by_name 根据列名 返回其列号
column_get_by_col_name 指定列名 获取整一列数据
column_hidden 隐藏列
records_get 从excel查询指定范围数据 返回字典
records_write 写入符合格式数据 [{},{}]
"""
import os
import shutil
import time
from functools import wraps
from zipfile import BadZipFile
import openpyxl
from openpyxl.cell.cell import Cell
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter
from .log_message import LogMessage, LOG_ERROR, LOG_DEBUG, LOG_WARN, LOG_INFO


def sheet_exist(func):
    """
    装饰器 在涉及表操作之前 先检查表是否存在 没有则创建
    注意 此装饰器的函数第一个参数不能作为关键字传参
    :param func:
    :return:
    """

    @wraps(func)
    def inner(*args, **kwargs):
        self = args[0]
        try:
            sheet_name = args[1]
            if sheet_name not in self.sheet_list:
                LogMessage(level=LOG_INFO, module="Excel", msg='sheet_name:"{}"不存在 新建~'.format(sheet_name))
                self.wb.create_sheet(sheet_name)
                self.save()
                self.sheet_list.append(sheet_name)
        except IndexError:
            LogMessage(level=LOG_ERROR, module="Excel", msg='方法:"{}"得一个参数请勿使用关键字传参'.format(func.__name__))
        res = func(*args, **kwargs)
        return res

    return inner


class Excel:
    def __init__(self, file_name, new_flag=False):
        """
        Excel 对openpyxl封装
        :param file_name: 需要操作的excel文件路径和名称
        :param new_flag: 如果file_name 不存在则新建，存在也不会覆盖
        """
        self.file_name = file_name
        if os.path.exists(self.file_name):
            try:
                self.wb = openpyxl.load_workbook(file_name)
            except BadZipFile as e:
                raise BadZipFile(f"Excel 文件损坏 ,{e} ...")
        else:
            if new_flag:
                self.wb = openpyxl.Workbook()
                LogMessage(level=LOG_INFO, module="Excel", msg='sheet_name:"{}"不存在 新建~'.format(self.file_name))
            else:
                LogMessage(level=LOG_ERROR, module="Excel", msg='sheet_name:"{}"不存在'.format(self.file_name))
        self.sheet_list = self.wb.sheetnames
        self.align = Alignment(horizontal="left", vertical="center")

    def save(self, backup=False) -> None:
        """
        新近啊或者保存excel文件
        :param backup:是否备份
        :return:
        """
        if backup:
            cur_time = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
            file_name = ".".join(self.file_name.split(".")[:-1])
            suffix = self.file_name.split(".")[:-1]
            shutil.copy(self.file_name, f'{file_name}_{cur_time}.{suffix}')
        LogMessage(level=LOG_DEBUG, module="Excel", msg='Save "{}"....'.format(self.file_name))
        try:
            self.wb.save(self.file_name)
        except PermissionError:
            LogMessage(level=LOG_ERROR, module="Excel", msg='Data won\'t be saved !!! Close excel file ,Please')

    def sheet_delete(self, sheet_name) -> None:
        """
        删除表
        :param sheet_name: 表名
        :return:
        """
        if sheet_name in self.sheet_list:
            sheet = self.sheet_handler(sheet_name)
            self.wb.remove(sheet)
            LogMessage(level=LOG_INFO, module="Excel", msg='Delete sheet:"{}"不存在'.format(sheet_name))
            self.save()
        else:
            LogMessage(level=LOG_ERROR, module="Excel", msg=f'Pass ,sheet: "{sheet_name}" is not in {self.sheet_list}')

    @sheet_exist
    def sheet_handler(self, sheet_name):
        """
        获取表对象 如果表名不在excel文件夹里 就创建
        :param sheet_name: 表吗名
        :return:
        """
        return self.wb[sheet_name] if sheet_name in self.sheet_list else self.wb.create_sheet(sheet_name)

    @sheet_exist
    def cell_handler(self, sheet_name, row: int, column: int) -> Cell:
        """
        获取单元格
        :param sheet_name: 表名
        :param row: 行数
        :param column: 列数
        :return: 单元格操作对象
        """
        sheet = self.sheet_handler(sheet_name)
        sheet[f"{get_column_letter(column)}{row}"].alignment = self.align  # 设置cell格式
        return sheet.cell(row, column)

    @sheet_exist
    def query(self, sheet_name, row_start=None, row_end=None, column_start=None, column_end=None, by="row"):
        """
        从excel查询指定范围数据
        :param sheet_name: 表名
        :param row_start: 开始行idx
        :param row_end: 结束行idx
        :param column_start: 开始列idx
        :param column_end: 结束列idx
        :param by: 生成行迭代器 生成列迭代器
        :return:
        """
        sheet = self.sheet_handler(sheet_name)
        if by == "row":
            child_sheet = sheet.iter_rows(min_row=row_start, max_row=row_end, min_col=column_start, max_col=column_end,
                                          values_only=True)
        else:
            child_sheet = sheet.iter_cols(min_row=row_start, max_row=row_end, min_col=column_start, max_col=column_end,
                                          values_only=True)
        return child_sheet

    @sheet_exist
    def row_insert(self, sheet_name, row_index, amount=1) -> None:
        """
        在指定行之上插入若干行
        :param sheet_name: 表名
        :param row_index: 行号
        :param amount: 行数
        :return:
        """
        sheet = self.sheet_handler(sheet_name)
        sheet.insert_rows(row_index, amount)
        LogMessage(level=LOG_DEBUG, module="Excel",
                   msg=f"Insert {amount} row(s) before row{row_index} in Sheet: {sheet_name}")

    @sheet_exist
    def row_delete(self, sheet_name, row_index, amount=1):
        """

        :param sheet_name: 表名
        :param row_index: 行号
        :param amount: 行数
        :return: 删除的行号
        """
        sheet = self.sheet_handler(sheet_name)
        sheet.delete_rows(row_index, amount)
        LogMessage(level=LOG_DEBUG, module="Excel",
                   msg=f"Delete {amount} row(s) before row{row_index} in Sheet: {sheet_name}")

    @sheet_exist
    def rows_delete_discrete(self, sheet_name, row_indexs: list):
        """
        根据行号 删除不连续的多行
        :param sheet_name: 表名
        :param row_indexs: 行号
        :return:
        """
        for row_index in sorted(row_indexs, reverse=True):  # 要从底部开始删除
            self.row_delete(sheet_name, row_index, 1)

    @sheet_exist
    def columns_name_get(self, sheet_name) -> dict:
        """
        将sheet第一列作为列名 显示所有的列名称对应的列数
        :param sheet_name: 表明
        :return: 所有列{名称：列标}
        """
        sheet = self.sheet_handler(sheet_name)
        try:
            columns_names = [cell.calue for cell in list(sheet.rows)[0]]
            return {k: v + 1 for v, k in enumerate(columns_names)}
        except IndexError:
            LogMessage(level=LOG_ERROR, module="Excel", msg="Empty Sheet")
            return dict()

    @sheet_exist
    def column_index_get_by_name(self, sheet_name, column_name, write_new_col=False) -> int:
        """
        根据列名 返回其列号
        如果没找到
        :param sheet_name:
        :param column_name:
        :param write_new_col:
        :return:
        """
