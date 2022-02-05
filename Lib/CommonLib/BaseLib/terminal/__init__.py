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


# 可能不准确
ENTER_CHAR = {"os": "\n", "bmc": "\n", "uefi": "\r\n", "scp": "\r\n", "mcp": "\r\n", "itos": "\r\n"}
GLB_ENTER_CHAR = {"Windows": "\r\n", "Linux": "\n", "Darwin": "\r"}
PATH_CONNECTOR = {"Windows": "\\", "Linux": "/", "Darwin": "/"}

# 先识别失败在识别成功
ERROR_RESULT_MAP = {
    r"excute error": {"retcode": 1, "retinfo": "error"},
    r"Invalid\s*Parameter": {"retcode": 2, "retinfo": "Invalid Parameter"},
    r"Missing\s*Parameter": {"retcode": 3, "retinfo": "Missing Parameter"},
    r"command\s*not\s*found": {"retcode": 4, "retinfo": "command not found"},
    r'No\s*such\s*file\s*or\s*directory': {"retcode": 127, "retinfo": "No such file or directory"},
    r"success": {"retcode": 0, "retinfo": "succ01"},

}


class Terminal:
    def __init__(self, host_type, host_ip, port, username, password, timeout, proxy=False, proxy_ip=None,
                 proxy_port=None, proxy_username=None, proxy_password=None, hold=False, baud_rate=115200,
                 view_mode=TermView.VIEW_OS, input_interval=0.1):
        """基本信息变量"""
        self.type = host_type.lower()
        self.host_ip = host_ip
        self.port = port
        self.timeout = timeout
        """连接状态"""
        self.is_connected = False
        if proxy and not all([proxy_ip, proxy_port, proxy_username, proxy_password]):
            raise Exception("需要输入代理信息")
        # 业务相关变量
        self.hold = hold  # 是否保持会话 用于交互操作 telnet 连注解方式只能为hold
        self.view_mode = view_mode
        enter_char = ENTER_CHAR.get(self.view_mode, ENTER_CHAR[TermView.VIEW_OS])
        if self.type == "telnet":
            self.term = Telnet(host_ip=host_ip, port=port, username=username, password=password, timeout=timeout,
                               proxy=proxy, proxy_ip=proxy_ip, proxy_port=proxy_port, proxy_username=proxy_username,
                               proxy_password=proxy_password, enter_char=enter_char, input_interval=input_interval,
                               view_mode=view_mode)
        elif self.type == "ssh":
            self.term = Ssh(host_ip=host_ip, port=port, username=username, password=password, timeout=timeout,
                            proxy=proxy, proxy_ip=proxy_ip, proxy_port=proxy_port, proxy_username=proxy_username,
                            proxy_password=proxy_password, hold=hold, enter_char=enter_char,
                            input_interval=input_interval,
                            )
        elif self.type == "com":
            self.term = Com(port=port, baud_rate=baud_rate, timeout=timeout)
        else:
            raise Exception(f"host_type {self.type} not supported yet Com SSH or Telnet are supported")

    def __repr__(self):
        return f"Terminal <{self.type} {self.host_ip}>"

    def connect(self) -> bool:
        """
        链接 term 本质是调用self.term.connect
        下层connect有失败信息 这里不做错误处理
        ssh尝试连接两次 telnet尝试连接三次 前两次使用实例化时传递的参数进行连接操作 第三次改变view mode进行连接
        :return:
        """
        connect_times = 0
        LogMessage(module="Terminal", msg=f"{self} connecting......")
        while not self.is_connected and connect_times <= 3:
            self.is_connected = self.term.connected()
            connect_times += 1
        if self.is_connected:
            LogMessage(module="Terminal", msg=f"{self} connected")
        else:
            LogMessage(level=LOG_ERROR, module="Terminal", msg=f"{self} connected fail")

        return self.is_connected

    def close(self) -> bool:
        if self.is_connected or self.term.is_connected:
            LogMessage(module="Terminal", msg=f"{self} disconnecting......")
            self.term.close()
            self.is_connected = False
            LogMessage(module="Terminal", msg=f"{self} disconnect successfully......")
        LogMessage(module="Terminal", msg=f"{self} is_connected: {self.term.is_connected}")
        return not self.is_connected

    def cmd_send(self, cmd, timeout=None, wait4res=True, delay_recv=0, ret_str='', wait4ret_str=False,
                 quite=False) -> dict:
        """

        :param cmd:
        :param timeout:  超时 默认使用self.timeout
        :param wait4res: 是否等待返回值 默认为True 为Flase时不接收返回值
        :param delay_recv:延迟接受数据 延迟delay_recv秒后接收数据
        :param ret_str:返回截断参数 在超时间内等待此字符
        :param wait4ret_str: ret_str有值时 这个参数才有意义！ 必须等到ret_str，才结束此时login_head不生效
        :param quite:是否打印结果到日志 默认为False
        :return:
        """
        timeout = self.timeout if timeout is None else timeout
        # 发送命令行 获取返回值
        try:
            cmd_ = cmd.replace(self.term.password, "* * *") if self.term.password else cmd
        except TypeError:
            cmd_ = cmd
        LogMessage(module="Terminal", msg=f"> {cmd_}")
        ret_txt = self.term.cmd_send(cmd=cmd, ret_str=ret_str, timeout=timeout, wait4res=wait4res,
                                     wait4ret_str=wait4ret_str, delay_recv=delay_recv)
        # 打印命令响应
        if not quite:
            LogMessage(module="Terminal", msg=f"\n< {ret_txt}")
        # 命令响应生成
        ret_dict = self.check_result(ret_txt)  # 判断命令行是否正确被执行 注意 这里不判断回显的个性化预期变量
        ret_dict["rettxt"] = ret_txt

        return ret_dict

    @staticmethod
    def check_result(ret_txt) -> dict:
        """检查term返回的string 是否含有错误信息"""
        ret_dict = {"retcode": 0, "retinfo": "succ01"}
        """命令执行结果 str 与默认指定的规格result_dict 进行匹配 匹配中则终止"""
        for key_word, ret in ERROR_RESULT_MAP.items():
            if re.search(key_word, ret_txt):
                ret_dict = ret
                break
        return ret_dict

    def file_exists(self, file_path):
        """
        判断terminal机器上指定路径 或者 文件是否存在
        :param file_path: 远程路径
        :return:
        """
        result = self.cmd_send(f"ls {file_path}")
        return True if re.search(r"No\s*such\s*file\s*or\s*directory", result["rettxt"]) is None else False

    def is_os_view(self):
        return self.view_mode == TermView.VIEW_OS

    def is_uefi_view(self):
        return self.view_mode == TermView.VIEW_UEFI

    def is_scp_view(self):
        return self.view_mode == TermView.VIEW_SCP

    def is_mcp_view(self):
        return self.view_mode == TermView.VIEW_MCP

    def is_bmc_view(self):
        return self.view_mode == TermView.VIEW_BMC

    def is_itos_view(self):
        return self.view_mode == TermView.VIEW_ITOS
