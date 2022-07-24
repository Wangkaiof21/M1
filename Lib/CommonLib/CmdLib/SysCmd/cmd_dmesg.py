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

    #  USB信息
    def usb(self):
        option = "usb"
        return self.grep_get(option)

    #  dma信息
    def dma(self):
        option = "dma"
        return self.grep_get(option)

    #  内存信息
    def memory(self):
        option = "memory"
        return self.grep_get(option)

    #  sata盤信息
    def sata(self):
        option = "sd"
        return self.grep_get(option)

    #  串行接口信息
    def tty(self):
        option = "tty"
        return self.grep_get(option)

    # cpu信息
    def cpu(self):
        option = "cpu"
        return self.grep_get(option)

    # 内核中link信息
    def link(self):
        option = "link"
        return self.grep_get(option)

    # 内核中網卡相關信息信息
    def eth(self):
        option = "eth"
        return self.grep_get(option)

    # 清空dmesg緩衝區日志信息，閲讀並清空所有信息
    def read_clean(self):
        option = "-c"
        return self.grep_get(option)

    # 清除内核缓冲区
    def clear(self):
        option = "-C"
        return self.grep_get(option)

    # 显示帮助信息
    def help(self):
        option = "-h"
        return self.grep_get(option)

    # 显示dmesg日志后n行
    def tail(self, lines_number=20):
        option = "| tail -" + str(lines_number)
        return self.grep_get(option)

    # 列出加载到内核的所有驱动
    def more(self):
        option = "| more"
        return self.grep_get(option)

    def less(self):
        option = "| less"
        return self.grep_get(option)

    # 显示打印信息之间的时间差
    def show_time_delta(self):
        option = "-d"
        return self.grep_get(option)

    # 显示本地时间和时间增量
    def reltime(self):
        option = "-e"
        return self.grep_get(option)

    # 显示内核消息
    def kernel_msg_display(self):
        option = "-k"
        return self.grep_get(option)

    # 打印原始信息缓冲
    def raw_message_buffer(self):
        option = "-r"
        return self.grep_get(option)

    # 强制使用syslog(2)而不是/dev/kmsg
    def force_use_syslog2(self):
        option = "-S"
        return self.grep_get(option)

    # 显示人类可读的时间戳
    def timestamp_show(self):
        option = "-T"
        return self.grep_get(option)

    # 显示用户信息
    def user_info_display(self):
        option = "-u"
        return self.grep_get(option)

    # 输出版本信息并退出
    def version_info_display(self):
        option = "-V"
        return self.grep_get(option)

    # 打印输出最近一次信息
    def last_msg_output(self):
        option = "| tail -f"
        return self.grep_get(option)

    # 将系统启动信息保存在文件中
    def file_saved(self, file="boot.messages"):
        option = "> {}".format(file)
        return self.grep_get(option)


if __name__ == '__main__':
    term = Terminal(host_type="ssh", host_ip='192.168.11.141', port=22, username='root', password='123123', proxy=True)
    term.connect()
    dmesg = CmdDmesg(term)
