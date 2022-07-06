#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/3/4 23:39
# @Author  : v_bkaiwang
# @File    : cmd_sysctl.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
from Lib.CommonLib.BaseLib.log_message import LogMessage, LOG_ERROR
from Lib.CommonLib.BaseLib.terminal import Terminal


class CmdSystemctl:
    def __init__(self, terminal=None):
        self.terminal = terminal if isinstance(terminal, Terminal) else LogMessage(level=LOG_ERROR,
                                                                                   module="CmdSystemctl", msg="Error")

    def randomize_va_space_set(self, value):
        """
        临时改变ASLR策略方法
        :param value:
        0 = 关闭
        1 = 半随机，共享库、栈、mmap()以及VDSD 将被随机化 PIE会影响heap的随机化
        2 = 全随机 除了1所述 还有heap
        :return:
        """
        cmd_set = f'echo {self.terminal.term.password}|sudo -S sysctl kernel.randomize_va_space={value}'
        self.terminal.cmd_send(cmd=cmd_set)
        cmd_check = 'cat /proc/sys/kernel/randomize_va_space'
        res4chk = int(self.terminal.cmd_send(cmd=cmd_check)['rettxt'])
        return res4chk == value


if __name__ == '__main__':
    test = CmdSystemctl(Terminal)
    test.randomize_va_space_set(value=2)
