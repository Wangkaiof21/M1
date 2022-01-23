#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/4 12:37
# @Author  : v_bkaiwang
# @File    : ssh.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
import re
import socket
import time
import paramiko
from Lib.ComminLib.log_message import LogMessage, LOG_ERROR, LOG_WARN, LOG_DEBUG


class Ssh:
    def __init__(self, host_ip, port=22, username=None, password=None, timeout=5, proxy=False,
                 proxy_ip=None, proxy_port=22, proxy_username=None, proxy_password=None,
                 input_interval=0.1, enter_char="\n", scale_factor=1, hold=False, called=False):
        # 基本信息
        self.hostname = host_ip
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
        self.ssh = paramiko.SSHClient()  # 创建一个ss客户端 连接服务器
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 创建白名单对象
        self.shell = None
        # 业务相关
        self.enter_char = enter_char  # 一般是回车
        self.login_head = ""  # 连接后的头部 登陆的用户@主机名:当前所在目录:权限
        self.scale_factor = scale_factor
        self.input_interval = input_interval * self.scale_factor  # 在uefi和itos下 命令输入的间隙
        self.ansi_esccape = re.compile(br'(?:\x1B[@-Z\\-_]|[\x80-\x9a\x9C-\x9f]|(?:\x1B\[|\x9B])[0-?]*[ -/]*[@-~])',
                                       re.VERBOSE)  # VT100 ANSI转义字符串正则
        self.default_buffer_size = 1024
        self.hold = hold
        self.called = called

    def connect(self) -> bool:
        try:
            if self.proxy:
                proxy_sock = self._get_proxy_sock()
                self.ssh.connect(hostname=self.hostname, username=self.username, password=self.password,
                                 sock=proxy_sock, timeout=self.timeout)
            else:
                self.ssh.connect(hostname=self.hostname, username=self.username, password=self.password,
                                 timeout=self.timeout)
            if self.hold:
                self.shell = self.ssh.invoke_shell(width=256)  # 引用一个shell维持会话
                self._receive()  # 尝试通过_receive更新 login head
            self.is_connected = True
            LogMessage(level=LOG_DEBUG, module="Ssh",
                       msg=f"connect to {self.hostname}:{self.port} successfully")
        except Exception as e:
            LogMessage(level=LOG_ERROR, module="Ssh",
                       msg=f"Failed to  connect  {self.hostname}:{e}")
        return self.is_connected

    def close(self) -> None:
        if self.is_connected:
            try:
                if self.shell:
                    self.shell.close()
                self.ssh.close()
                self.is_connected = False
                LogMessage(level=LOG_DEBUG, module="Ssh",
                           msg=f"SSH: {self.hostname}:{self.port} close")
            except Exception as e:
                LogMessage(level=LOG_ERROR, module="Ssh",
                           msg=f"SSH: {self.hostname}:{self.port} close failed {e}")

    def cmd_send(self, cmd: str, ret_str="", wait4ret_str=False, timeout=5, wait4res=True, delay_recv=0) -> str:
        """

        :param cmd:
        :param ret_str:
        :param wait4ret_str: ret_str 有值时 此参数才有意义 必须等到ret_str 才结束此时login head 不生效
        :param timeout:
        :param wait4res: 是否等待结果 ssh非hold情况才有意义
        :param delay_recv: 延迟接收
        :return:
        """
        command_result = ""
        if not self.is_connected:
            LogMessage(level=LOG_ERROR, module="Ssh",
                       msg=f"SSH: {self.hostname}:{self.port} is Connected yet , Please check again")
            return command_result

        if self.called or self.hold:
            command_result = self._exec_command(cmd, timeout=timeout, ret_str=ret_str, wait4ret_str=wait4ret_str,
                                                delay_recv=delay_recv)
        else:
            stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=timeout)
            if not wait4res:
                return command_result
            for line in stderr.read_lines():
                command_result += line
            for line in stdout.read_lines():
                command_result += line
                if ret_str and (ret_str in command_result):
                    break
        return command_result

    def _exec_command(self, cmd, timeout, delay_recv, ret_str, wait4ret_str) -> str:
        """执行命令返回 sh+telnet ssh hold/called模式下会调用此方法"""
        for i in range(0, len(cmd), 20):
            self.shell.send(cmd[i:i + 20])
            time.sleep(self.input_interval)
        self.shell.send(self.enter_char)
        time.sleep(delay_recv)
        result = self._receive(timeout=timeout, ret_str=ret_str, wait4ret_str=wait4ret_str)
        result = result.replace(cmd.strip(), "").replace(self.login_head, "").strip()
        return result

    def _get_proxy_sock(self):
        """建立ssh代理通路"""
        proxy_ssh = paramiko.SSHClient()
        proxy_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        proxy_ssh.connect(hostname=self.proxy_ip, username=self.proxy_username, password=self.proxy_password,
                          timeout=self.timeout)
        LogMessage(level=LOG_DEBUG, module="Ssh",
                   msg=f"connect to proxy: {self.proxy_ip}:{self.proxy_port} successfully")
        vm_transport = proxy_ssh.get_transport()
        remot_address = (self.hostname, self.port)
        local_address = (self.proxy_ip, self.proxy_port)
        vm_channel = vm_transport.open_channel("direct_tcpip", remot_address, local_address)
        return vm_channel

    @property
    def _pattern(self):
        return re.compile(rf'.*?{self.username}[@:]*.*?[\n]*[#$]|Shell>|\w+:\\>|ali2600:[~/].*[#$]')

    def _receive(self, timeout=None, ret_str="", wait4ret_str=False) -> str:
        """ 接收返回值（包含更新login head的业务）ssh+telnet ssh hold/called模式下会调用此方法"""
        self.shell.timeout = timeout if timeout else self.timeout
        result = b''  # 最终结果
        last_res = b''  # 上一次临时返回值 用于quite = Ture状况
        buffer_size = 500 * 1024
        while True:
            time.sleep(0.5)
            """读取shell里的内容"""
            try:
                tmp_res = self.shell.recv(buffer_size)
                LogMessage(level=LOG_DEBUG, module="_receive", msg=f"{tmp_res.__sizeof__()},{buffer_size}\n{tmp_res}")
                if tmp_res.__sizeof__() >= buffer_size:
                    LogMessage(level=LOG_WARN, module="_receive", msg=f"buffsize no enough")
                tmp_res = self.ansi_esccape.sub(b'', tmp_res)
                match_tmp = b''.join([last_res, tmp_res])
                last_res = tmp_res
                result += tmp_res
            except socket.timeout:
                LogMessage(level=LOG_WARN, module="_receive", msg=f"shell receive timeout, {self.shell.timeout}")
                break
            """处理读取的result 判断是否正常结束循环"""
            if wait4ret_str and ret_str:  # wait4ret_str = Ture ret_str 有值时  login_head在result也不返回
                if ret_str in match_tmp.decode("utf-8", errors="ignore"):
                    break
            else:  # 通过login head判断是否返回
                login_head_match = self._pattern.search(match_tmp.decode("utf-8", errors="ignore"))
                LogMessage(level=LOG_DEBUG, module="ssh", msg=f"login head match{login_head_match}")
                if login_head_match:
                    if self.login_head != login_head_match.group():  # 判断login head是否要更新
                        self.login_head = login_head_match.group()
                        LogMessage(level=LOG_DEBUG, module="_receive",
                                   msg=f"refresh login head to {repr(self.login_head)}")
                        break
        return result.decode("utf-8", errors="ignore")
