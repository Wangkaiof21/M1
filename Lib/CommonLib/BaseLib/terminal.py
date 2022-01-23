#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/14 19:30
# @Author  : v_bkaiwang
# @File    : terminal.py
# @Software: win10 Tensorflow1.13.1 python3.6.3

import re
import os

from GlobalConfig.global_config import TermCfg
from Lib.ComminLib.BaseLib.ssh import Ssh
from Lib.ComminLib.BaseLib.com import Com
from Lib.ComminLib.BaseLib.telnet import Telnet
from Lib.ComminLib.BaseLib.log_message import LogMessage, LOG_INFO, LOG_ERROR
from Lib.ComminLib.BaseLib.cmd_template import NormalTable, NormalTxt, str_get, table_get


class TermView:
    VIEW_OS = 'os'
    VIEW_BMC = 'bmc'
    VIEW_UEFI = 'uefi'
    VIEW_SCP = 'scp'
    VIEW_MCP = 'mcp'
    VIEW_ITOS = 'itos'


ENTER_CHAR = {'os': '\n', 'bmc': '\n', 'uefi': '\r\n', 'scp': '\r\n', 'mcp': '', '\r\n': '', 'itos': '\r\n'}

result_dict = {r'excut error': {"retcode": 1, "retinfo": "error"},
               r'Invalid\s*Parameter': {"retcode": 2, "retinfo": "Invalid Parameter"},
               r'Missing\s*Parameter': {"retcode": 3, "retinfo": "Missing Parameter"},
               r'command\s*not\s*found': {"retcode": 4, "retinfo": "command not found"},
               r'No\s*such\s*file\s*or\s*directory': {"retcode": 127, "retinfo": "No such file or directory"},
               r'success': {"retcode": 0, "retinfo": "succ01"},
               }


class Terminal:
    def __init__(self, host_type=TermCfg.GLB_HOST_TYPE, host_ip='127.0.0.1', port=None, username='', password='',
                 timeout=5, proxy=False, proxy_ip=TermCfg.GLB_PROXY_HOST,
                 proxy_port=TermCfg.GLB_PROXY_PORT, proxy_username=TermCfg.GLB_PROXY_USER, input_interval=0.1,
                 proxy_password=TermCfg.GLB_PROXY_PWD, ret_str="", hold=False, baud_rate=115200,
                 view_mode=TermView.VIEW_OS):

        self.timeout = timeout

        self.proxy = proxy
        self.proxy_ip = proxy_ip
        self.proxy_port = proxy_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password

        self.host_ip = host_ip
        self.port = port
        self.username = username
        self.password = password

        self.name = host_ip + ":" + str(port)
        self.type = host_type.lower()
        self.ret_str = ret_str
        self.scale_factor = TermCfg.GLB_SCALE_FACTOR
        self.is_connected = False
        self.hold = hold
        self.view_mode = view_mode
        # enter_char为'\n'  不合适时使用默认enter_char
        self.enter_char = ENTER_CHAR.get(self.view_mode, ENTER_CHAR[TermView.VIEW_OS])

        # 注意支持链接类型的connect ，cmd_send 返回参数要一致
        if self.type == 'telnet':
            self.term = Telnet(host_ip=self.host_ip, port=self.port, username=self.username, password=self.password,
                               timeout=self.timeout, proxy=self.proxy, proxy_ip=self.proxy_ip,
                               proxy_port=self.proxy_port, proxy_username=self.proxy_username,
                               proxy_password=self.proxy_password, ret_str=ret_str, enter_char=self.enter_char,
                               input_interval=input_interval, view_mode=view_mode
                               )

        elif self.type == 'ssh':
            self.term = Ssh(host_ip=self.host_ip, port=self.port, username=self.username, password=self.password,
                            timeout=self.timeout, proxy=self.proxy, proxy_ip=self.proxy_ip,
                            proxy_port=self.proxy_port, proxy_username=self.proxy_username,
                            proxy_password=self.proxy_password, hold=self.hold, ret_str=self.ret_str,
                            enter_char=self.enter_char,
                            input_interval=input_interval, view_mode=view_mode)

        elif self.type == 'com':
            self.term = Com(port=self.port, baudrate=baud_rate, timeout=self.timeout, write_timeout=self.timeout)
        else:
            LogMessage(level=LOG_ERROR, module='Terminal', msg=f"{self.type} no supported (yet.com, ssh or telnet)")

    def connect(self):
        # 下层connect 已经有失效信息 此处不处理
        # ss尝试连接两次 telnet尝试三次  前两次实例化传递信息操作 第三次改变view_mode尝试连接
        for i in range(2):
            if not self.is_connected:
                try:
                    self.is_connected = True if self.term.connect() else False
                except Exception as e:
                    LogMessage(level=LOG_ERROR, module='Terminal', msg=f"{e}")
            else:
                break
        else:
            if not self.is_connected:
                if self.view_mode == 'telnet':
                    old_view_mode = self.term.view_mode
                    self.term.view_mode = 'uefi' if self.view_mode == 'os' else 'os'
                    LogMessage(level=LOG_ERROR, module='Terminal', msg=f"{old_view_mode}"
                               f" 与当前环境不符合 已切换成 {self.view_mode}")
                    self.term.enter_char = ENTER_CHAR.get(self.term.view_mode, ENTER_CHAR[self.term.view_mode])
                    self.is_connected = True if self.term.connect() else False
            else:
                self.is_connected = True if self.term.connect() else False

        if self.type == 'telnet':
            LogMessage(level=LOG_INFO, module='Terminal', msg=f"Telnet connected :{self.host_ip}:{self.port}")
        elif self.type == 'ssh':
            LogMessage(level=LOG_INFO, module='Terminal', msg="SSH connected :{}".format(self.term.is_connected))
        else:
            LogMessage(level=LOG_INFO, module='Terminal', msg="SSH connected :{}".format(self.term.is_connected))
        if not self.is_connected:
            LogMessage(level=LOG_ERROR, module='Terminal', msg=" connected Failed ! Please check proxy or connected")
        return self.is_connected

    def close(self):
        if not self.is_connected:
            LogMessage(level=LOG_ERROR, module='Terminal', msg="connected :{}".format(self.is_connected))
        else:
            self.term.close()
            self.is_connected = False
            LogMessage(level=LOG_ERROR, module='Terminal', msg=f"Disconnect :{self.type} successfully")
            LogMessage(level=LOG_ERROR, module='Terminal', msg=f"check {self.type} connect status {self.is_connected}")

    def cmd_send(self, cmd, ret_str=None, var_map=None, template=None, timeout=None, wait4res=True, wait4res_str=False,
                 max_loop_time=3, quiet=False, delay_recv=0):
        """

        :param cmd:
        :param ret_str: 返回值参数
        :param var_map:
        :param template:
        :param timeout:
        :param wait4res:是否等待返回值 默认为True 为false 不接受任何返回值
        :param wait4res_str: （极其特殊场景）ret_str有值时 此参数才有意义！！！ 必须等待ret_str，才算结束，此时login_head不生效
        :param max_loop_time:
        :param quiet: 设为False 则不打印结果到日志
        :param delay_recv: 延迟接收数据
        :return:
        """
        if not var_map:
            var_map = dict()
        if not ret_str:
            ret_str = self.ret_str

        if timeout is None:
            timeout = self.timeout
        # 设置降频系数
        timeout *= self.scale_factor
        # send command
        try:
            LogMessage(level=LOG_INFO, module='Terminal', msg=cmd.replace(os.getenv('PASSWD'), '***'))
        except TypeError:
            LogMessage(level=LOG_ERROR, module='Terminal', msg=cmd)

        result = self.term.cmd_send(cmd=cmd, ret_str=ret_str, timeout=timeout, wait4res=wait4res,
                                    wait4res_str=wait4res_str, max_loop_time=max_loop_time, quiet=quiet,
                                    delay_recv=delay_recv)
        if not quiet:
            LogMessage(level=LOG_INFO, module='Terminal', msg=f'\n{result}')

        # 判断命令是否执行正确
        ret_dict = self.check_result(result)
        ret_dict['rettxt'] = result

        # 按照消息打印内容
        ret_value_list = []
        if template:
            ret_value_list = self.var_get(result, var_map=var_map)
        ret_dict['retvalues'] = ret_value_list
        return ret_dict

    @staticmethod
    def check_result(string):
        # 默认值为不成功
        result = {"retcode": 0, "retinfo": "succ01"}
        # 命令行执行结果str与默认指定判断规格result_dict进行匹配， 匹配中则终止
        if not isinstance(string, bool):
            for key_word in result_dict:
                if re.search(key_word, string):
                    result = result_dict[key_word]
                    break
        else:
            if not string:
                result = result_dict['excut error']
        return result

    @staticmethod
    def var_get(string, var_map=None, template=NormalTxt):
        """

        :param string:
        :param var_map:
        :param template:
        :return:
        """
        result = None
        if NormalTxt == template:
            result = str_get(txt_str=string, var_map=var_map, split_char=':')
            pass
        elif NormalTable == template:
            result = str_get(txt_str=string, var_map=var_map, split_char=':')
            pass
        else:
            LogMessage(level=LOG_ERROR, module='Terminal', msg=f'msg template is not supported yet, please refer to '
                       f'file, ')

        return result

    def file_exist(self, file_path):
        """
        判断Terminal上的文件是否存在
        :param file_path:
        :return:
        """

        result = self.cmd_send("ls {}".format(file_path))
        return True if re.search(r'No\s*such\s*file\s*or\s*directory', result["rettxt"])is None else False

    def is_os_view(self):
        return self.view_mode == TermView.VIEW_OS

    def is_bmc_view(self):
        return self.view_mode == TermView.VIEW_BMC

    def is_uefi_view(self):
        return self.view_mode == TermView.VIEW_UEFI

    def is_scp_view(self):
        return self.view_mode == TermView.VIEW_SCP

    def is_mcp_view(self):
        return self.view_mode == TermView.VIEW_MCP

    def is_itos_view(self):
        return self.view_mode == TermView.VIEW_ITOS


if __name__ == '__main__':
    from GlobalConfig.global_config import TermCfg
    from Lib.ComminLib.CoreLib.msg_center import MsgCenter
    from Lib.FeatureLib.PerfLib.perf_config import PerTermCfg

    MsgCenter(testcase_name="Terminal")
    term = Terminal(host_type='ssh', host_ip='11.165.150.221', port=22, username=PerTermCfg.GLB_USER,
                    password=PerTermCfg.GLB_PASSWORD, proxy=False, hold=True)

    term.connect()
    result_test = term.cmd_send("ls")
    print(result_test)








