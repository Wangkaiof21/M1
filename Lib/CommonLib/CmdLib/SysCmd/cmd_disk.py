#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/3/4 23:36
# @Author  : v_bkaiwang
# @File    : cmd_disk.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
from Lib.ComminLib.BaseLib.log_message import LogMessage, LOG_ERROR
from Lib.ComminLib.BaseLib.terminal import Terminal


class CmdDisk:
    def __init__(self, terminal=None):
        self.terminal = terminal if isinstance(terminal, Terminal) else LogMessage(level=LOG_ERROR, module='CmdDisk')

    def details_get(self, all_='', mb_size='', type_='', inode='', local='', by=''):
        """
        查看磁盘整体情况
        :param all:默认为空
        :param mb_size:
        :param type:
        :param inode:
        :param local:
        :param by:显示方式 默认是‘h’ 按照较易读GB KB MB等格式显示
        :return:返回整体磁盘情况
        """
        cmd = 'df -{}{}{}{}{}{}'.format(all_, by, mb_size, type_, inode, local)
        # 执行cmd获取结果
        cmd_result = self.terminal(cmd=cmd)
        return cmd_result
