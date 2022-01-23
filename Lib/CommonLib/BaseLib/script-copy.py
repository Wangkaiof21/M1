#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/17 17:44
# @Author  : v_bkaiwang
# @File    : script-copy.py
# @Software: win10 Tensorflow1.13.1 python3.6.3

import os
import argparse
import openpyxl

"""
name for flags - 一个命名或者一个选项字符串的列表 例如 foo 或者 -f -foo
action - 当参数在命令行出现使用的动作基本类型
nargs - 命令行参数消耗的相应数目
const - 被一些 action 和 nargs 选择所需求的常数
default - 当参数未在命令行出现时用的值
type - 命令行参数应当被转换的类型
choices - 可用的参数容器
required - 此命令行选项 是否可以省略
help - 一个此选项的简单描述
metavar - 在使用方法消息中去使用的参数值示例
dest - 被添加到parse_args() 所返回的对象的属性名
"""


class Excel:
    def __init__(self, file_name):
        """
        Excel类 对openpyxl封装
        :param file_name: 需要操作的excel文件路径和名称
        """
        self.file_name = file_name
        if os.path.exists(self.file_name):
            # excel 工作簿操作对象
            self.wb = openpyxl.load_workbook(self.file_name)
        else:
            raise FileNotFoundError(f'没有找到{self.file_name}')
        self.sheet_list = self.wb.sheetnames

    def sheet_handler(self, sheet_name):
        """
        设置表操作对象 如果表明不在excel中 就创建
        :param sheet_name: 表名
        :return:
        """
        return self.wb[sheet_name] if sheet_name in self.sheet_list else self.wb.create_sheet(sheet_name)

    def cell_handler(self, sheet_name, row, column, value_only=False):
        """
        设置单元格操作对象
        :param sheet_name:表名
        :param row: 行
        :param column:列
        :param value_only:是否返回cell值
        :return: 单元格操作对象
        """
        sheet = self.sheet_handler(sheet_name)
        return sheet.cell(row, column).value if value_only else sheet.cell(row, column)

    def query(self, sheet_name, row_start=0, row_end=0, column_start=0, column_end=0, by='row'):
        """
        从Excel查询指定范围数据
        :param sheet_name: 表名
        :param row_start: 开始行
        :param row_end: 结束行
        :param column_start: 开始列
        :param column_end: 结束列
        :param by: row 生成行迭代器， col 生成列迭代器
        :return:
        """
        sheet = self.sheet_handler(sheet_name)
        # 如果没传row_end/column_end 则默认传最大行/最大列
        row_end = sheet.max_row if not row_end else row_end
        column_end = sheet.max_column if not column_end else row_end
        # 表格指定范围的生成器
        if by == 'row':
            child_sheet = sheet.iter_rows(min_row=row_start, max_row=row_end, min_col=column_start, max_col=column_end,
                                          values_only=True)
        else:
            child_sheet = sheet.iter_rows(min_row=row_start, max_row=row_end, min_col=column_start, max_col=column_end,
                                          values_only=True)
        return child_sheet

    def all_column_name(self, sheet_name):
        """
        将sheet第一行作为列名
        :param sheet_name:
        :return:
        """
        sheet = self.sheet_handler(sheet_name)
        col_names = [cell.value for cell in list(sheet.rows)[0]]
        return {k: v + 1 for v, k in enumerate(col_names)}

    def colname_index(self, sheet_name, column_name):
        """
        根据列名 返回列号
        :param sheet_name:
        :param column_name:
        :return:
        """
        col_names = self.all_column_name(sheet_name)
        if col_names:
            try:
                return col_names[sheet_name]
            except KeyError:
                raise KeyError(f'not found col_name {column_name} in sheet {col_names.keys()}')

        else:
            raise FileNotFoundError(f'空列表{sheet_name}')

    def column_get_by_col_name(self, sheet_name, column_name):
        """
        指定列名 获取整列的信息
        :param sheet_name:表名
        :param column_name:列名
        :return:
        """
        sheet = self.sheet_handler(sheet_name)
        col_index = column_name if isinstance(column_name, int) else self.colname_index(sheet_name, column_name)
        column_generator = self.query(sheet_name, row_start=0, row_end=sheet.max_row, column_start=col_index,
                                      column_end=col_index, by='column')
        res_list = list(list(column_generator)[0])
        return res_list


class FileCopy:
    def __init__(self):
        # 公共参数
        self.parent_parser = argparse.ArgumentParser(add_help=False)
        self.parent_parser.add_argument('excel_file', help='excel file path')
        self.parent_parser.add_argument('sheet', help='sheet of being copied case number')
        self.parent_parser.add_argument('-ad', help='script directory', required=True, dest='aim_dir')
        self.parent_parser.add_argument('-c', help='check', dest='check')

        self.parser = argparse.ArgumentParser(description='Script Copy Tool')
        subparsers = self.parser.add_subparsers(help='子命令使用方法')

        parser_scripts_copy = subparsers.add_parser('script_copy', parernts=[self.parent_parser], help='script_copy')
        parser_scripts_copy.add_argument('-t', dest='total', action='store_true',
                                                    help='if copy all (include config & script)')

        parser_scripts_copy.set_defaults(function=self.scripts_copy)
        parser_conf_set = subparsers.add_parser('conf_set', parernts=[self.parent_parser], help='conf_set')
        parser_conf_set.set_defaults(function=self.conf_set)
        self.args = self.parser.parse_args()
        self.excel_file = self.args.excel_file
        self.sheet = self.args.sheet
        self.excel = Excel(self.excel_file)
        self.excel_sheets = self.excel.sheet_list
        self.all_col_names = self.excel.all_column_name(self.sheet)
        self.args = self.parser.parse_args()
        print(self.__dict__['args'])

    @staticmethod
    def _replace(olds: list, news: list, content: bytes):
        """
        :param olds:
        :param news:
        :param content:
        :return:
        """
        olds_length = len(olds)
        news_length = len(news)
        assert olds_length == news_length, f'Different length {olds}. {news}'
        for i in range(olds_length):
            content = content.replace(olds[i].encode('utf-8'), news[i].encode('utf-8'))
        return content

    def _item4modify(self):
        args = list(self.all_col_names.keys())
        olds_list = []
        news_list = []
        for i in range(0, len(args), 2):
            olds_list.append(self.excel.column_get_by_col_name(self.sheet, args[i][1:]))
            news_list.append(self.excel.column_get_by_col_name(self.sheet, args[i + 1][1:]))
        return olds_list, news_list

    def _script_copy(self):
        """
        要修改的地方只有类名 config导包路径
        :return:
        """
        _old, _new = self._item4modify()
        for i in range(len(_old[0])):
            old_tc_num = _old[0][i]
            new_tc_num = _new[0][i]

            old_file_name = os.path.join(self.args.aim_dir, f'test_{old_tc_num}_Script.py')
            old_class_name = f'Test{old_tc_num.title().replace("_", "")}Script'
            old_config_name = f'test_{old_tc_num}_config'

            new_file_name = os.path.join(self.args.aim_dir, f'test_{new_tc_num}_Script.py')
            new_class_name = f'Test{new_tc_num.title().replace("_", "")}Script'
            new_config_name = f'test_{new_tc_num}_config'

            olds = [old_class_name, old_config_name]
            news = [new_class_name, new_config_name]

            for j in range(1, len(_old)):
                olds.append(_old[j][i])
                news.append(_new[j][i])

            print(f'{os.path.basename(old_file_name)}-------------->{os.path.basename(new_file_name)}')
            with open(old_file_name, 'rb') as r:
                tmp = "\n".join(r.read().decode('utf-8').splitlines()).encode('utf-8')
                with open(new_file_name, 'wb') as w:
                    w.write(self._replace(olds, news, tmp))

    def _config_copy(self):
        """
        config 需要修改的只有tc_num 就是用例编号
        :return:
        """
        _old, _new = self._item4modify()
        for i in range(len(_old[0])):
            old_tc_num = _old[0][i]
            new_tc_num = _old[0][i]

            old_testcase_name = old_tc_num
            old_file_name = os.path.join(self.args.aim_dir, f'test_{old_tc_num}_config.py')
            old_num = f'编号{old_tc_num.split("_")[-1]}'

            new_testcase_name = new_tc_num
            new_file_name = os.path.join(self.args.aim_dir, f'test_{new_tc_num}_config.py')
            new_num = f'编号{new_tc_num.split("_")[-1]}'

            olds = [old_num, old_testcase_name]
            news = [new_num, new_testcase_name]

            for j in range(1, len(_old)):
                olds.append(_old[j][i])
                news.append(_new[j][i])

            print(f'{os.path.basename(old_file_name)}   --->  {os.path.basename(new_file_name)}')
            with open(old_file_name, 'rb') as r:
                tmp = "\n".join(r.read().decode('utf-8').splitlines()).encode('utf-8')
                with open(new_file_name, 'wb') as w:
                    w.write(self._replace(olds, news, tmp))

    def _files_copy(self, config_copy=False):
        if self.sheet not in self.excel_sheets:
            raise FileNotFoundError(f'Not Found {self.sheet} in {self.args.excel_file}')
        self._script_copy()
        if config_copy:
            self._config_copy()

    def _sys_conf_set(self):
        if self.sheet not in self.excel_sheets:
            raise FileNotFoundError(f'Not Found {self.sheet} in {self.args.excel_file}')

        _old, _new = self._item4modify()
        for i in range(len(_old[0])):
            old_file = _old[i][0]
            new_file = _new[i][0]

            old_file_path = os.path.join(self.args.aim_dir, old_file)
            new_file_path = os.path.join(self.args.aim_dir, new_file)

            olds = []
            news = []

            for j in range(1, len(_old)):
                olds.append(_old[j][i])
                news.append(_new[j][i])

            print(f'{os.path.basename(old_file_path)}   --->  {os.path.basename(new_file_path)}')
            with open(old_file_path, 'rb') as r:
                tmp = "\n".join(r.read().decode('utf-8').splitlines()).encode('utf-8')
                with open(new_file_path, 'wb') as w:
                    w.write(self._replace(olds, news, tmp))

    def check(self):
        pass

    def scripts_copy(self):
        self._files_copy(config_copy=self.args.total)
        if self.args.checl():
            self.check()
        else:
            pass

    def conf_set(self):
        # 配置修改方法
        self._sys_conf_set()
        pass


fc = FileCopy()
fc.args.func()

# 使用方法
# 拷贝脚本: python script-copy.py script_copy excel路径 sheet名称 -ad 目标路径
# 拷贝脚本+配置: python script-copy.py script_copy excel路径 sheet名称 -ad 目标路径 -t
# 变更系统配置: python script-copy.py conf_set excel路径 sheet名称 -ad 目标路径

