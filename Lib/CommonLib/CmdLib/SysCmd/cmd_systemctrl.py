#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/3/4 23:39
# @Author  : v_bkaiwang
# @File    : cmd_systemctrl.py
# @Software: win10 Tensorflow1.13.1 python3.6.3

import os
from Lib.ComminLib.BaseLib.log_message import LogMessage, LOG_INFO, LOG_ERROR
from Lib.ComminLib.BaseLib.terminal import Terminal


class CmdSysCtrl:
    def __init__(self, terminal=None):
        self.terminal = terminal if isinstance(terminal, Terminal) else LogMessage(level=LOG_ERROR, msg="CmdSysCtrl")
        self.passwd = os.getenv('PASSWD')

    def server_status(self, server_name):
        """
        查询服务器状态
        :param server_name:
        :return:
        """
        cmd = f'echo {self.passwd}|sudo -S systemctl status {server_name}'
        LogMessage(level=LOG_INFO, msg=self.terminal.cmd_send(cmd))
        return self.terminal.cmd_send(cmd)

    def server_start(self, server_name):
        """
        启动服务
        :param server_name:
        :return:
        """
        cmd = f'echo {self.passwd}|sudo -S systemctl start {server_name}'
        LogMessage(level=LOG_INFO, msg=self.terminal.cmd_send(cmd))
        return self.terminal.cmd_send(cmd)

    def server_stop(self, server_name):
        """
        停止服务
        :param server_name:
        :return:
        """
        cmd = f'echo {self.passwd}|sudo -S systemctl stop {server_name}'
        LogMessage(level=LOG_INFO, msg=self.terminal.cmd_send(cmd))
        return self.terminal.cmd_send(cmd)

    def server_restart(self, server_name):
        """
        重启服务
        :param server_name:
        :return:
        """
        cmd = f'echo {self.passwd}|sudo -S systemctl restart {server_name}'
        LogMessage(level=LOG_INFO, msg=self.terminal.cmd_send(cmd))
        return self.terminal.cmd_send(cmd)
