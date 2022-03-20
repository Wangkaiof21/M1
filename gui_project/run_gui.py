# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/3/20 10:30
# @Author  : v_bkaiwang
# @File    : run_gui.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
import configparser
import os
from tkinter import *
import time
from tkinter import font as tk_font
import subprocess
import threading
import sys

WINDOW_SIZE = '900x700+450+50'
LOG_LINE_NUM = 0
Log_file = r'./logs/test_result.log'
fail_case = r'./logs/fail_case.txt'
con_file = r'./config.ini'
# 默网站地址
WEB_URL = 'http://172.168.121.131:8080/120116/qy'
USER_NAME = '120116'
PASS_WD = 'admin123'
PROJECT_ID = USER_NAME


# 默认测试数据路径
TEST_CASE_FILE_PATH = r'G:\自动化\测试用例\FK\访客系统接口.xlsx'
# 默认数据库信息
DATA_BASE_PATH = '172.168.120.116'
DB_USER = 'root'
DB_PASS_WD = '123'
DB_NAME = 'c3_qy'
LEVEL = ''


class MyGui():
    def __init__(self, init_window):
        self.init_window = init_window
        self.font_type = tk_font.Font(family='Fixdsys', size=10, weight=tk_font.BOLD)
        self.init_window.title("接口测试工具")  # 窗口名
        self.init_window.geometry(WINDOW_SIZE)  # 窗体大小
        # 输入框
        label_row = 0
        # step1 设置位置
        # 实例化了一个Label
        self.host_label = Label(self.init_window, text="网站地址:", font=self.font_type)
        # 使用grid布局器 进行性网格划分
        self.host_label.grid(row=label_row, column=0, sticky=E, padx=5, pady=12)
        # step2 设置输入框的类别 和填充基本内容
        # 网站地址
        default_web = StringVar()
        default_web.set(WEB_URL)
        self.web_host = Entry(self.init_window, width=35, textvariable=default_web)
        self.web_host.grid(row=label_row, column=1)

        # 多租户项目id
        label_row = label_row + 1
        self.project_id_label = Label(self.init_window, text="租户号:", font=self.font_type)
        self.project_id_label.grid(row=label_row, column=0, sticky=E, padx=5, pady=0)
        default_project_id = StringVar()
        default_project_id.set(PROJECT_ID)
        self.en_project_id = Entry(self.init_window, width=35, textvariable=default_project_id)
        self.en_project_id.grid(row=label_row, column=1)


def gui_start():
    # 添加环境变量
    now_path = os.getcwd()
    if now_path not in sys.path:
        sys.path.insert(0, now_path)
    # 实例化出一个父窗口
    init_window = Tk()
    # 设置根窗口默认属性
    MyGui(init_window)
    # 父窗口进入事件循环，可以理解为保持窗口运行，否则界面不展示
    init_window.mainloop()


if __name__ == '__main__':
    gui_start()
