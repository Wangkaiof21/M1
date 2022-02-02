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
        self.ansi_escape = re.compile(br'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])',
                                      re.VERBOSE)

    def connect(self) -> bool:
        if self.proxy:
            return self._connect_with_proxy()
        else:
            return self._connect()

    def close(self) -> None:
        if self.is_connected:
            try:
                self.tn.close()
                self.is_connected = False
                LogMessage(level=LOG_DEBUG, module="Telnet", msg=f"Telnet:{self.host_ip}:{self.port} closed !")
            except Exception as e:
                LogMessage(level=LOG_DEBUG, module="Telnet",
                           msg=f"Telnet:{self.host_ip}:{self.port} closed failed !!! {e}")

    def login_head_refresh(self):
        """
        刷新login head
        :return:
        """
        self.tn.write(f'{self.enter_char}'.encode("utf-8", errors="ignore"))
        # 临时超时时间 用于建立连接后 输入回车 获取返回值
        tmp_timeout = self.scale_factor * 0.5
        # 遇到symbol4chk 就停止接收
        tmp_res = self.tn.read_until(f"{self._symbol4chk}".encode("utf-8", errors="ignore"), timeout=tmp_timeout)
        # 用''替换ansi转义序列
        tmp_res = self.ansi_escape.sub(b'', tmp_res).decode("utf-8", errors="ignore")
        # 匹配login_head正则
        login_heads = self._pattern.findall(tmp_res)

        if login_heads:
            self.login_head = login_heads[0]
            LogMessage(level=LOG_DEBUG, module="Telnet", msg=f"login head change to {self.login_head}")
        else:
            LogMessage(level=LOG_ERROR, module="Telnet", msg=f"未登陆成功，或有其他人在操作此机器")
        return self.login_head

    def cmd_send(self, cmd, timeout=5, wait4res=True, delay_recv=0, ret_str='', wait4ret_str=False):
        """

        :param cmd:
        :param timeout:
        :param wait4res:
        :param delay_recv:
        :param ret_str:
        :param wait4ret_str:
        :return:
        """
        # wait4ret_str 暂未使用（对于直连 无proxy的telnet场景 暂不使用）
        # self.proxy 为true时 这里self.tn.cmd_send 本质上是ssh 在 hold模式下调用cmd_send
        if self.proxy:
            return self.tn.cmd_send(cmd=cmd, timeout=timeout, wait4res=wait4res, ret_str=ret_str,
                                    wait4ret_str=wait4ret_str, delay_recv=delay_recv)
        else:
            return self._cmd_send(cmd=cmd, timeout=timeout, wait4res=wait4res, ret_str=ret_str,
                                  wait4ret_str=wait4ret_str, delay_recv=delay_recv)

    @property
    def _pattern(self):
        """login_head 用pattern"""
        return re.compile(rf'.*?{self.username}[@:]*.*?[\n]*[#$]|Shell>|\w+:\\>')

    @property
    def _symbol4chk(self) -> str:
        """命令提示符的结束符"""
        if self.view_mode in ["itos", "uefi"]:
            symbol4chk = '>'
        # elif self.username == 'root':
        #     symbol4chk = "#"
        else:
            symbol4chk = '$'

        return symbol4chk

    def _connect_with_proxy(self) -> bool:
        """本质上是ssh类，Telnet代理模式(ssh+telnet，由执行机连接telnet)，本质上是hold模式下调用cmd_send"""
        self.tn = Ssh(host_ip=self.proxy_ip, port=self.port, username=self.username, password=self.password,
                      called=True, hold=True, enter_char=self.enter_char, input_interval=self.input_interval)
        self.tn.connect()
        # todo: 在shell里telnet以后loginhead的username与telnet的username不一致，暂时写死telnet机器为root用户 后续考虑优化
        self.tn.username = 'root'
        res = self.tn.cmd_send(f'telnet {self.host_ip} {self.port}{self.enter_char}')
        # 如果返回值中出现telnet 则说明命令的返回值未被replace(ssh.py的_exec_command方法会replace掉命令和loginhead) 认为未连接成功
        self.is_connected = False if 'telnet' in res else True
        return self.is_connected

    def _connect(self) -> bool:
        """telnet直连"""
        try:
            self.tn = telnetlib.Telnet(host=self.host_ip, port=self.port, timeout=self.timeout)
        except ConnectionRefusedError or OSError as e:
            LogMessage(level=LOG_ERROR, module="Telnet",
                       msg=f"端口错误 failed to connect to {self.host_ip}:{self.port}\n Error:{e}")
            return self.is_connected
        except OSError as e:
            LogMessage(level=LOG_ERROR, module="Telnet",
                       msg=f"IP错误 failed to connect to {self.host_ip}:{self.port}\n Error:{e}")
            return self.is_connected
        # # TODO:暂时未调通 telnet需要用户名和场景
        # if self.username:
        #     self.tn.read_until(b'login:',timeout=self.timeout)
        #     self.tn.write(f'{self.username}{self.enter_char}'.encode("utf-8", errors="ignore"))

        self._check_first_login()
        return self.is_connected

    def _check_first_login(self):
        """
        直连用
        创建telnet对象后 敲回车 看是否返回'shell>','root@wing:~#' 或 '[root@xx /]'(login_head)字符
        如果能返回字符 则说明成功
        :return:
        """
        login_head = self.login_head_refresh()
        # 刚telnet链接进入 依据'>' 判断shell或者是uefi..; '#'(root权限)判断为os 后期还有普通用户登录haps则为'$'
        # 此处判断enter_char/view_mode 是否与当前系统相符
        if self._symbol4chk not in login_head:
            self.is_connected = False
            return self.is_connected
        if login_head:
            self.is_connected = True
            LogMessage(level=LOG_DEBUG, module="Telnet", msg=f"connect to {self.host_ip}:{self.port} successfully !")
        else:
            LogMessage(level=LOG_ERROR, module="Telnet", msg=f"connect to {self.host_ip}:{self.port} failed !")
        return self.is_connected

    def _cmd_send(self, cmd, timeout, wait4res, ret_str, wait4ret_str, delay_recv):
        """
        向串口发送命令 并打印回显
        :param cmd: 发送命令的字段
        :param timeout: 超时
        :param wait4res:
        :param ret_str: 遇到该字段立即返回 不再读取数据
        :param wait4ret_str:
        :param delay_recv:
        :return:
        """
        result = b''
        if not self.is_connected:
            LogMessage(level=LOG_ERROR, module="Telnet",
                       msg=f"Telnet {self.host_ip}:{self.port} is not Connected yet ! Please check again !")
            return result
        # 清理超时cmd命令遗留的buf
        self.tn.read_eager()
        for i in range(0, len(cmd), 20):
            self.tn.write(cmd[i:i + 20].encode("utf-8", errors="ignore"))
            time.sleep(self.input_interval)
        self.tn.write(self.enter_char.encode("utf-8", errors="ignore"))
        if not wait4res:
            # 比如起iperf任务就不需返回值 直接返回''
            return result
        time.sleep(delay_recv)
        # 回读信息
        try:
            # 如果wait4ret_str 为True 则等待ret_str
            if wait4ret_str and ret_str:
                result = self.tn.read_until(ret_str.encode("utf-8", errors="ignore"), timeout=timeout)
            else:
                result = self.tn.read_until(self.login_head.encode("utf-8", errors="ignore"), timeout=timeout)
        except TimeoutError:
            LogMessage(level=LOG_ERROR, module="Telnet", msg=f"connect timeout {cmd}")
        result = self.ansi_escape.sub(b'', result).decode("utf-8", errors="ignore")
        # result 包含的cmd 和 login_head 在这里剔除
        result = result.replace(cmd.strip(), '').replace(f'{self.enter_char}{self.login_head}', '').strip()
        return result
