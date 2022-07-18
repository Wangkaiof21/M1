#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/3/4 23:36
# @Author  : v_bkaiwang
# @File    : cmd_dmesg.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
from Lib.CommonLib.BaseLib.log_message import LogMessage, LOG_ERROR
from Lib.CommonLib.BaseLib.terminal import Terminal


class CmdDmesg:
    def __init__(self, terminal=None):
        self.terminal = terminal if isinstance(terminal, Terminal) else LogMessage(level=LOG_ERROR, module="CmdDmesg",
                                                                                   msg="Terminal is not isinstance of Terminal")

    def dmesg(self, option="", timeout=5):
        """
        设置及操作类的调用
        :param option: 选项参数
        :param timeout: 超时设置
        :return:
        """
        # 核心命令：发送命令
        cmd = "dmesg {}".format(option)
        self.terminal.cmd_send(cmd=cmd, timeout=timeout)

    def get(self, option="", timeout=5):
        """
        获取有回显数据调用
        :param option: 选项参数
        :param timeout: 超时设置
        :return:
        """
        cmd = "dmesg {}".format(option)
        cmd_result = self.terminal.cmd_send(cmd=cmd, timeout=timeout)
        ret = cmd_result["rettxt"]
        return ret

    # 查询网卡信息
    def nic_exception_msg_get(self, timeout=5):
        """
        查询网卡异常信息
        :param timeout:超时
        :return: 元组
        """
        judged_flag = False
        option = "-T |grep -E 'eth|enp'"
        first_data = self.get(option, timeout=timeout)
        out_data = ""
        if ("fail" or "err" or "warn" or "unsupport") in first_data:
            LogMessage(level=LOG_ERROR, module="nic_exception_msg_get", msg=">>> EXCEPTION MESSAGE:")
            option += "| grep -iE 'fail|err|warn|unsupport'"
            judged_flag = True
            out_data = self.get(option, timeout=timeout)
            return judged_flag, out_data
        else:
            LogMessage(level=LOG_ERROR, module="nic_exception_msg_get", msg=">>> NO EXCEPTION MESSAGE!")
            return judged_flag, out_data

    @func_name_wrapper
    def devices_exception_check(self, device):
        """
        设备异常故障检查
        :param device:
        :return:
        """
        pass_wd = self.terminal.term.password
        # TODO: error; unsupport->nosuppor
        cmd = f'echo {pass_wd} |sudo -S dmesg |grep -E {device} |grep -iE \'fail|error|warn|unsupport\'|wc -l'
        cmd_result = self.terminal.cmd_send(cmd=f'bash --login -c "{cmd}"')['rettxt']
        cmd_result = int(cmd_result.split(':')[-1].strip())
        return True if not cmd_result else False

    def grep_get(self, option):
        """

        :param option:
        :return:
        """
        new_option = " -T |grep -i" + option
        ret_text = self.get(new_option)
        grep_name = option
        grep_data = []
        for temp_data in ret_text.splitline():
            if grep_name in temp_data:
                grep_data.append(temp_data)
                grep_data.append("\n")
        return "".join(grep_data)

    def usb(self):
        option = "usb"
        return self.grep_get(option)

