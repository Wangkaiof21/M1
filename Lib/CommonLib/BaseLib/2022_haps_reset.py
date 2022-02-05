#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/5 18:24
# @Author  : v_bkaiwang
# @File    : 2022_haps_reset.py
# @Software: win10 Tensorflow1.13.1 python3.6.3

# reboot脚本

# 刷新bios版本

import re
import time

import os
from Lib.CommonLib.log_message import LogMessage, LOG_DEBUG
from Lib.CommonLib.CoreLib.msg_center import MsgCenter
from Lib.CommonLib.BaseLib.terminal import Terminal

FILE_NEME = os.path.splitext(os.path.basename(__file__))[0]
MsgCenter(testcase_name="REBOOT", level=LOG_DEBUG)
while True:
    term = Terminal(host_type='ssh', timeout=5, host_ip='183.233.222.243', port=22456, username='mtest',
                    password='mtest', hold=True)
    term.connect()
    res = term.cmd_send('telnet_evb_ap 107')
    print(repr(res['rettxt']))
    res = term.cmd_send('\n')
    ret_txt = res['rettxt'].replace("", "")
    print(repr(ret_txt))
    if 'login' in ret_txt:
        term.cmd_send('root')
        term.cmd_send('Alibaba%1688')
        term.cmd_send('reboot')
    elif '/root' in ret_txt:
        term.cmd_send('reboot')
    else:
        term.cmd_send('reset\r\n')
    term.close()


