#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/4 12:37
# @Author  : v_bkaiwang
# @File    : telnet.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
# 终端控制类 负责链接各类终端 并下发命令和返回信息
import re
import telnetlib
import time

from ..log_message import LogMessage, LOG_DEBUG, LOG_ERROR
from .ssh import Ssh


# 由于存在ANSI导致readuntil方法使用异常
class TelnetWithoutANSI(telnetlib.Telnet):
    def process_rwaq(self):
        super().process_rawq()
        # ANSI转义相关
        ansi_escape = re.compile(br'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])',
                                 re.VERBOSE)
        # 把原有的成员变量cookedg,sbdataq中的ansi转义去掉
        self.cookedq = ansi_escape.sub(b'', self.cookedq)
        self.sbdataq = ansi_escape.sub(b'', self.sbdataq)

    def read_until(self, match, timeout=None):
        buf = super().read_until(match, timeout=None)
        if match not in buf:
            raise TimeoutError('timeout')
        return buf


telnetlib.Telnet = TelnetWithoutANSI


class Telnet:
    def __init__(self, host_ip, port, username=None, password=None, timeout=5, proxy=False,
                 proxy_ip=None, proxy_port=22, proxy_username=None, proxy_password=None,
                 input_interval=0.1, enter_char="\n", view_mode="os", scale_factor=1):
        # 基本信息
        self.host_ip = host_ip
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        # 代理
        self.proxy = proxy
        self.proxy_ip = proxy_ip
        self.proxy_port = proxy_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        # 状态
        self.is_connected = False
        # 底层对象
        self.tn = None
        # 业务相关变量
        self.enter_char = enter_char
        self.view_mode = view_mode
        self.login_head = ""  # 命令提示符 登陆当前主机@用户名:当前目录所在地:用户权限
        self.scale_factor = scale_factor
        self.input_interval = input_interval * self.scale_factor  # 在uefi和itos下 命令输入的间隙
        self.ansi_esccape = re.compile(br'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])',
                                       re.VERBOSE)

    def connect(self) -> bool:
        if self.proxy:
            return self._connect_with_proxy()
        else:
            return self_connect()

    def close(self) -> None:
        if self.is_connected:
        try:
            self.tn.close()
            self.is_connected=False
            LogMessage(level=LOG_DEBUG,module="Telnet",msg=f"Telnet:{self.host_ip}:{self.port} closed !")
        except Exception as e:
            LogMessage(level=LOG_DEBUG, module="Telnet", msg=f"Telnet:{self.host_ip}:{self.port} closed failed !!! {e}")



    def login_head_refresh(self):
        """
        刷新login head
        :return:
        """
        self.tn.write(f'{self.enter_char}'.encode("utf-8", errors="ignore"))
        #
