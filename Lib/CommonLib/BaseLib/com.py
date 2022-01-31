#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/6 19:52
# @Author  : v_bkaiwang
# @File    : com.py
# @Software: win10 Tensorflow1.13.1 python3.6.3

import time
import serial
import traceback

# 创建了GlobalConfig.globalconfig则解开注释
from Lib.ComminLib.BaseLib.log_message import * # CommonLib.BaseLib.log_message import LogMessage, Log_ERROR, Log_INFO, LOG_WARN|
from GlobalConfig.globalconfig import OrtherCfg


class Com:
    def __init__(self, port, baudrate, timeout=3, write_timeout=3):
        self.port = port
        # 波特率 标准值之一
        self.baudrate = baudrate
        self.timeout = timeout
        self.write_timeout = write_timeout
        self.ser = None
        self.is_connected = False

    def connect(self):
        """
        打开串口 并找到串口对象
        :return:
        """
        # TODO:python3版本均使用pyserial，不再使用serial
        try:
            self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout,
                                     write_timeout=self.write_timeout)
        except Exception:
            LogMessage(level=LOG_ERROR, module="Class com", msg="Serial open faild")
        LogMessage(level=LOG_INFO, module="Class com", msg="Serial open successed")
        LogMessage(level=LOG_INFO, module="Class com", msg=str(self.ser))
        self.is_connected = True
        return self.is_connected

    def cmd_send(self, cmd, ret_str, timeout, wait4res=None, wait4res_str=None,
                 max_loop_time=None, quiet=None, delay_recv=0):
        """
        cmd向串口发送命令 并取回命令打印信息
        :param cmd: 待发送字符串
        :param ret_str: 遇到该字符串立即返回，不再继续读取数据
        :param timeout: 超时，即使没遇到ret_str也要返回
        :param wait4res:
        :param max_loop_time:
        :param quiet:
        :return:
        """
        if not self.ser:
            return ""
        # 发送命令前 检查缓存 先清空缓存
        count = self.ser.in_waiting
        if count:
            string = self.ser.read(count).decode('utf-8', errors='ignore')
            LogMessage(level=LOG_INFO, module="Class com", msg="清理缓存残留数据" + string)

        cmd = cmd + OrtherCfg.GLB_ENTER_CHAR['Linux']
        # 发送命令
        try:
            self.ser.write(cmd.encode('utf-8', errors='ignore'))
        except Exception:

            LogMessage(level=LOG_ERROR, module="Class com", msg="SendCmd faild" + traceback.format_exc())
            # traceback.format_exc()异常定位函数
            return ""
        # 回读返回信息
        ret = ""
        t_tatal = 0
        t_step = 0.5
        while True:
            count = self.ser.in_waiting
            if count > 0:
                ret += (self.ser.read(count).replace(b'\r', b'')).decode('utf-8', errors='ignore')
                # 判断是否遇到退出字符
            if ret.find(ret_str) > 0:
                break
            time.sleep(t_step)
            t_tatal = t_tatal + t_step
            # 判断是否超时
            if t_tatal < timeout:
                continue
            else:
                break
        return ret

    def msg_read(self, timeout):
        """
        回读信息
        :param timeout:
        :return:
        """
        ret = ""
        t_tatal = 0
        t_step = 0.5

        while True:
            count = self.ser.in_waiting
            if count > 0:
                ret += (self.ser.read(count)).decode('utf-8', errors='ignore')
            time.sleep(t_step)
            t_tatal = t_tatal + t_step
            # 判断是否超时
            if t_tatal < timeout:
                continue
            else:
                break
        return ret

    def close(self):
        self.ser.close()
        self.is_connected = False
        return self.is_connected

if __name__ == '__main__':
    com1 = Com("/dev/ttys0", 115200, 3)
    ret = com1.connect()
    ret1 = com1.cmd_send("ifconfig", "$", 5)

