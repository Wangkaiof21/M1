#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/4 12:36
# @Author  : v_bkaiwang
# @File    : __init__.py.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
"""
终端控制类
负责连接各类终端
下发命令和返回信息
"""
import re
from .com import Com
from .ssh import Ssh
from .telnet import Telnet
from ..log_message import LOG_ERROR, LogMessage


class TermView:
    VIEW_OS = "os"
    VIEW_BMC = "bmc"
    VIEW_UEFI = "uefi"
    VIEW_SCP = "scp"
    VIEW_MCP = "mcp"
    VIEW_ITOS = "itos"


