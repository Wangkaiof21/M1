#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/4 12:36
# @Author  : v_bkaiwang
# @File    : com.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
from time import sleep, time
import serial
from Lib.ComminLib.log_message import LOG_ERROR, LOG_INFO, LogMessage


class Com:
    def __init__(self, port, baud_rate, timeout=5):
        """

        :param port: 端口
        :param baud_rate: 波特率
        :param timeout: 超时时间
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout if timeout else 5
        self.password = ""
        self.login_head = ""
        self.ser = None

    @property
    def is_connected(self):
        if self.ser is None:
            return False
        return self.ser.is_open

    def connected(self):
        """打开串口 获取串口对象 更新login_head"""
        try:
            self.ser = serial.Serial(port=self.port, baudrate=self.baud_rate, timeout=self.timeout,
                                     write_timeout=self.timeout)
            self._login_head_fresh()
        except Exception as e:
            LogMessage(level=LOG_ERROR, module="Com", msg=f"Serial open Failed ...{e}")
            return self.is_connected
        LogMessage(level=LOG_INFO, module="Com", msg=f"{self.ser}\nopen successed...")
        return self.is_connected

    def cmd_send(self, cmd: str, ret_str="", wait4ret_str=None, timeout=None, wait4res=None, delay_recv=1):
        """
        向串口发送命令 返回信息
        :param cmd:
        :param ret_str: 遇到该字符串立即返回 不在读取
        :param wait4ret_str:
        :param timeout:
        :param wait4res:
        :param delay_recv:
        :return:
        """
        ret = ""
        if not self.is_connected:
            LogMessage(level=LOG_INFO, module="Com", msg="Com未连接或者断开")
            return ""
        timeout = timeout if timeout else self.timeout
        tmp = self._msg_read()  # 发送命令前 检查缓存 清空缓存
        if tmp:
            LogMessage(level=LOG_INFO, module="Com", msg="清理缓存残留数据" + tmp)
        cmd = cmd + "\r"
        try:
            self.ser.write(cmd.encode())
            sleep(1 + delay_recv)  # 等待in_waiting更新
        except Exception as e:
            LogMessage(level=LOG_ERROR, module="Com", msg=f"send cmd failed:{e}")
            return ret
        if not wait4res:
            return ret
        ret = self._msg_read(timeout=timeout, ret_str=ret_str, wait4ret_str=wait4ret_str)
        ret = ret.replace(cmd.strip(), "").replace(self.login_head, "")

    def close(self) -> bool:
        """关闭串口"""
        self.ser.close()
        return not self.is_connected

    def _msg_read(self, timeout=0, ret_str="", wait4ret_str=False):
        """
        回读信息包 cmd login_head
        :param timeout:
        :param ret_str: 遇到字符串立即返回
        :param wait4ret_str:
        :return:
        """
        ret = ""
        timeout = timeout if timeout else self.timeout
        t = time()
        while self.ser:
            tmp = self.ser.read(self.ser.in_waiting).decode()
            ret += tmp
            if wait4ret_str and ret_str in ret:
                break
            if time() - t > timeout:
                LogMessage(level=LOG_ERROR, module="Com", msg=f"msg read timeout!")
                break
        ret = ret.replace("\r\r", "\r")
        return ret

    def _login_head_fresh(self):
        self.login_head = self.cmd_send('')
        LogMessage(level=LOG_INFO, module="Com", msg=f"login head change to {self.login_head}")


if __name__ == '__main__':
    com1 = Com("com1", 38400)
    com1.connected()
    ret1 = com1.cmd_send("ifconfig")
    print(ret1)
