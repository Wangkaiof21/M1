#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/7 0:02
# @Author  : v_bkaiwang
# @File    : telnet.py
# @Software: win10 Tensorflow1.13.1 python3.6.3

import time
import re
import telnetlib

from GlobalConfig.global_config import TermCfg
from Lib.ComminLib.BaseLib.log_message import LogMessage, LOG_INFO, LOG_ERROR
from Lib.ComminLib.BaseLib.ssh import Ssh


class TelnetWithoutANSI(telnetlib.Telnet):
    def process_rawq(self):
        super().process_rawq()
        # ANSI转义相关正则类
        ansi_escape = re.compile(br'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])',
                                 re.VERBOSE)
        # 把原有的成员变量 cooked sbdatag中的ansi转义去除
        self.cookedq = ansi_escape.sub(b'', self.cookedq)
        self.sbdatag = ansi_escape.sub(b'', self.sbdatag)

    def read_until(self, match, timeout=None):
        buf = super().read_until(match, timeout)
        if match not in buf:
            raise TimeoutError('timeout')
        return buf


# 自定义去除ansi转义
telnetlib.Telnet = TelnetWithoutANSI


class Telnet:

    def __init__(self, host_ip, port, username=None, password=None, timeout=5, ret_str='', proxy=False,
                 proxy_ip=TermCfg.GLB_PROXY_HOST, proxy_port=TermCfg.GLB_PROXY_PROT, input_interval=0.1,
                 proxy_username=TermCfg.GLB_PROXY_USER, proxy_password=TermCfg.GLB_PROXY_PWD, enter_char=None,
                 view_mode='os'):

        self.tn = None
        self.host_ip = host_ip
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout

        self.proxy = proxy
        self.proxy_ip = proxy_ip
        self.proxy_port = proxy_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password

        self.is_connected = False
        self.name = host_ip + ":" + str(port)
        self.enter_char = enter_char
        self.view_mode = view_mode
        self.scale_factor = TermCfg.GLB_SCALE_FACTOR
        self.ret_str = ret_str
        self.timeout_flag = False

        self.login_head = ''  # 命令提示符 user@moker:/user/bin
        self.pattern = re.compile(rf'.*?{self.username}[@:]*.*[\n]*[#$]|Shell>|\w+:\\>')
        self.ansi_escape = re.compile(br'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])',
                                      re.VERBOSE)
        self.input_interval = input_interval * self.scale_factor

    @property
    def symbol4chk(self):
        """命令提示结束符"""
        if self.view_mode in ['itos', 'uefi']:
            symbol4chk = '>'
        else:
            symbol4chk = '$'
        return symbol4chk

    def connect(self):
        if self.proxy:
            # telnet代理模式 （ssh+telnet，由执行机链接telnet） 本质是ssh的hold模式
            return self._connect_with_proxy()
        else:
            return self._connect()

    def _connect_with_proxy(self):
        """
        本质上使用ssh类
        :return:
        """
        self.tn = Ssh(host_ip=self.proxy_ip, port=self.proxy_port, username=self.username,
                      password=self.proxy_password, called=True, hold=True, enter_char=self.enter_char,
                      input_interval=self.input_interval, view_mode=self.view_mode)
        self.tn.connect()
        # 在shell里的telnet 以后的loginhead的username与telnet里的username不一致，暂时写死telnet机器作为root用户
        self.tn.username = 'root'
        res = self.tn.cmd_send(f'telnet {self.host_ip} {self.port}{self.enter_char}')
        # 如果返回值中出现telnet 则说明命令返回值未被replace(ssh.py 的 _exec_command 会replace掉命令和loginhead)认为未连接成功
        self.is_connected = False if 'telnet' in res else True
        return self.is_connected

    def _check_first_login(self):
        """
        创建telnet对象后 敲回车 看是否能返回‘shell>’ 'root@wing:~#' 或者 [root@xxx /] 之类的loginhead字符串
        能返回则说明成功
        :return:
        """
        login_head = self.login_head_fresh()
        # 刚telnet链接进入 依据 '>' 判断是shell/uefi...; root权限判断为os 普通用户登录haps滋味‘$’
        # 此处判断enter_enter/view_mode 是否与系统相符
        if self.symbol4chk not in login_head:
            self.is_connected = False
            return self.is_connected

        if login_head:
            self.is_connected = True
            LogMessage(level=LOG_INFO, module='Telnet', msg=f"login to host:{self.name} successfully")
        else:
            LogMessage(level=LOG_ERROR, module='Telnet', msg=f"login to host:{self.name} failed")
        return self.is_connected

    def login_head_fresh(self):
        """
        刷新loginhead
        :return:
        """
        self.tn.write(f'{self.enter_char}'.encode('utf-8', errors='ignore'))
        # 临时的超时时间 用于获取建立连接后 输入回车 获取返回值 如果不加可能发生无法正常返回值 发现‘#’会终止等待
        tmp_timeout = self.scale_factor * 0.5
        # 遇到symbol4chk 就结束接收
        check_res = self.tn.read_until(f'{self.symbol4chk}'.encode('utf-8', errors='ignore'), timeout=tmp_timeout)
        # 转义 并正则匹配
        tmp_res = self.ansi_escape.sub(b'', check_res).decode('utf-8', errors='ignore')
        login_heads = self.pattern.findall(tmp_res)

        if login_heads:
            self.login_head = login_heads[0]
            LogMessage(level=LOG_INFO, module='Telnet', msg=f"login_head has change to :{self.login_head} ")
        else:
            LogMessage(level=LOG_ERROR, module='Telnet', msg=f"login to failed: 有人在操作此机器")

        return self.login_head

    def _connect(self):
        """
        telnet 直连
        :return:
        """
        try:
            self.tn = telnetlib.Telnet(host=self.host_ip, port=self.port, timeout=self.timeout)
        except ConnectionRefusedError as e:
            LogMessage(level=LOG_INFO, module='Telnet', msg=f"failed to connect to host :{self.name} \n "
                       f"Error : {e} 端口错误")
            return self.is_connected

        except OSError as e:
            LogMessage(level=LOG_INFO, module='Telnet',
                       msg=f"failed to connect to host :{self.name} \n Error : {e} IP错误")
            return self.is_connected

        self._check_first_login()
        return self.is_connected

    def cmd_send(self, cmd, ret_str='', timeout=5, wait4res=True, wait4res_str=False, max_loop_time=3, quiet=False,
                 delay_recv=0):
        """

        :param cmd:
        :param ret_str:
        :param timeout:
        :param wait4res:
        :param wait4res_str:
        :param max_loop_time:
        :param quiet:
        :param delay_recv:
        :return:
        """
        # wait4ret_str 暂未使用（对于直连 无代理telnet场景，暂不使用）
        # self.proxy 为True时 这里的self.tn.cmd_send 本质上时ssh 在hold模式下调用cmd_send
        if self.proxy:
            return self.tn.cmd_send(cmd, ret_str, timeout, wait4res, wait4res_str, max_loop_time, quiet, delay_recv)
        else:
            return self._cmd_send(cmd, ret_str, timeout, wait4res, wait4res_str, delay_recv)

    def _cmd_send(self, cmd, ret_str='', timeout=5, wait4res=True, wait4res_str=False, max_loop_time=3,delay_recv=0):
        """
        向串口发送命令 并取回打印信息
        :param cmd:
        :param ret_str: 遇到字符串 立即返回
        :param timeout:
        :param wait4res:
        :param wait4res_str:
        :param max_loop_time:
        :param delay_recv:
        :return:
        """

        command_result = ''
        # 如果telnet还未连接 则报错 并返回空字符串
        if not self.is_connected:
            LogMessage(level=LOG_INFO, module='Telnet',
                       msg=f"Telnet :{self.name} is not Connected yet")
            return command_result
        
        # 清理超时cmd命令遗留buf
        if self.timeout_flag and self.login_head.encode('utf-8', errors='ignore') in self.tn.read_eager():
            self.timeout_flag = False
        # 发现os下也会出现丢字符情况
        for i in range(0, len(cmd), 20):
            self.tn.write(cmd[i:i + 20].encode('utf-8', errors='ignore'))
            time.sleep(self.input_interval)
        self.tn.write(self.enter_char.encode('utf-8', errors='ignore'))
        
        if not wait4res:
            return command_result
        # 回读信息
        try:
            # 如果wait4res_str为True则等待ret_str
            if wait4res_str:
                command_result = self.tn.read_until(ret_str.encode('utf-8', errors='ignore'), timeout=timeout)
            else:
                command_result = self.tn.read_until(self.login_head.encode('utf-8', errors='ignore'), timeout=timeout)
                if b'Exception' in command_result:
                    command_result = False

        except TimeoutError:
            LogMessage(level=LOG_INFO, module='Telnet', msg=f"{cmd} command timeout")
            command_result = b''
            self.timeout_flag = True
            
        if not isinstance(command_result, bool):
            # 用‘’ 代替ansi转义
            tmp_res = self.ansi_escape.sub(b'', command_result).decode('utf-8', errors='ignore')
            # resul 包含的 cmd loginhead在此剔除
            command_result = tmp_res.replace(f'{self.enter_char}{self.login_head}', '').replace(f'{cmd}', '').strip()
        return command_result
    
    def read_msg(self, timeout):
        # 回读信息
        ret = ' '
        t_total = 0
        t_step = 0.5
        # 如果telnet还未连接 则报错 并返回空字符串
        if not self.is_connected:
            LogMessage(level=LOG_INFO, module='Telnet',
                       msg=f"Telnet :{self.name} is not Connected yet")
            return ret

        while True:
            rettxt = self.tn.read_very_eager()
            ret += rettxt
            LogMessage(level=LOG_INFO, module='Telnet', msg=rettxt)
            time.sleep(t_step)
            t_total = t_total + t_step
            if t_total < timeout:
                continue
            else:
                break
        return ret

    def close(self):
        if self.is_connected:
            try:
                self.tn.close()
                self.is_connected = False
                LogMessage(level=LOG_INFO, module='Telnet', msg=f'Telnet {self.name} close!')
            except Exception as e:
                LogMessage(level=LOG_INFO, module='Telnet', msg=f'Telnet {self.name} close Failed! Error message :{e}')


if __name__ == '__main__':
    from Lib.ComminLib.CoreLib.msg_center import MsgCenter
    MsgCenter(testcase='Telnet')
    term = Telnet(host_ip='1xxxxxxx', port=22, proxy=False)
    term.connect()
    res = term.cmd_send('', timeout=3600, ret_str='[root@', wait4res_str=True, quiet=True)
    term.close()
