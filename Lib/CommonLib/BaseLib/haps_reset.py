#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/16 18:17
# @Author  : v_bkaiwang
# @File    : haps_reset.py # reset脚本
# @Software: win10 Tensorflow1.13.1 python3.6.3

import os
import re
import sys
import time

sys.path.append((os.path.dirname((os.path.abspath('__file__')))).split("Lib")[0])

from GlobalConfig.global_config import TermCfg as Term
from Lib.ComminLib.BaseLib.terminal import Terminal
from Lib.ComminLib.BaseLib.log_message import LogMessage, LOG_INFO, LOG_ERROR
from Lib.ComminLib.CoreLib.msg_center import MsgCenter


class Reset:
    def __init__(self):
        self.term_uefi = Terminal(host_type='telnet', host_ip=Term.GLB_HOST, port=Term.GLB_PORT, view_mode='uefi',
                                  proxy=Term.GLB_PROXY)
        self.term_os = Terminal(host_type='telnet', host_ip=Term.GLB_HOST, port=Term.GLB_PORT, view_mode='os',
                                proxy=Term.GLB_PROXY)
        self.terms = Terminal(host_type='ssh', host_ip=Term.GLB_HOST, port=Term.GLB_PORT,
                              username=Term.GLB_PROXY_USER, password=Term.GLB_PROXY_PWD, hold=True, proxy=False)

    def haps_reset(self, fs=None, start_file=None, enter_environment=False, iautos=False):
        """

        :param fs: 挂载盘 FS0: FS2: FS3:
        :param start_file:需要执行的文件 start.nsh 进入的操作系统类别
        :param enter_environment:是否进入 os.itos
        :param iautos:c环境执行
        :return:

        """
        self.terms.connect()
        self.terms.cmd_send(cmd=f'haps_reset {Term.GLB_HAPS_INDEX}', timeout=3 * 60)  # 3min
        ret = self.terms.cmd_send(cmd=f'haps_telnet {Term.GLB_HAPS_INDEX}', timeout=20 * 30, ret_str="Shell",
                                  wait4res_str=True)['rettxt']
        if fs is None:
            # 获取默认最大FS
            res = re.findall(r'(FS\d:)', ret)
            res.sort()
            fs = res[-1]
        if start_file is None:
            start_file = "start_b030.nsh"
        self.terms.close()

        if enter_environment:
            self.term_uefi.connect()
            self.term_uefi.cmd_send(cmd=f'{fs}', timeout=60, ret_str=f'{fs}\> ', wait4res_str=True)
            self.term_uefi.term.login_head_fresh()
            ret = self.term_uefi.cmd_send(cmd='ls', timeout=60)['rettxt']
            if start_file in ret:
                self.term_uefi.cmd_send(cmd=f'{start_file}', timeout=60 * 60, ret_str="[root@", wait4res_str=True,
                                        quiet=True)
            else:
                LogMessage(level=LOG_INFO, module='haps_reset', msg=f"{start_file} : 该文件不存在 请检查版本号")

        if iautos:
            self.term_os.connect()
            self.term_os.cmd_send(cmd=f'{fs}', timeout=60, ret_str=f'{fs}\> ', wait4res_str=True)
            self.term_os.term.login_head_fresh()
            ret = self.term_os.cmd_send(cmd='ls', timeout=60)['rettxt']
            if start_file in ret:
                self.term_os.cmd_send(cmd=f'{start_file}', timeout=25 * 60)
            else:
                LogMessage(level=LOG_INFO, module='haps_reset', msg=f"{start_file} : 该文件不存在 请检查版本号")

            ret = self.term_uefi.cmd_send(cmd='itosrun -lf', timeout=6 * 60)['rettxt']
            res = re.findall(r'gic_automation : (.*)\n', ret)[0]

            # self.term_uefi.cmd_send(cmd=f'itosrun -s 0 {res}', timeout=6 * 60)

        self.term_uefi.close()

    def init_haps(self, hard_disk='sda4', nic=None):
        """
        B032 40M 版本配置
        :param hard_disk:
        :param nic:
        :return:
        """
        self.term_os.connect()
        self.term_os.cmd_send('echo 3600000 > /sys/block/sda/queue/io_timeout', timeout=60 * 60)
        self.term_os.cmd_send('echo 1 4 1 7 > /proc/sys/kernel/printk', timeout=60 * 60)

        # 网络配置
        if nic is None:
            time.sleep(3)
            ret = self.term_os.cmd_send('ip link show')['rettxt']
            nic = re.findall(r'(\d:\s[\w]*:)', ret)[1]
            nic = (nic.replace(" ", "")).split(":")[1]

        self.term_os.cmd_send(f"ip link set {nic} up")
        self.term_os.cmd_send(f'ip addr add {Term.GLB_HAPS_IP}/16 dev {nic}')

        # rootfs 切换
        self.term_os.cmd_send(f"cd /")
        self.term_os.login_head_fresh()
        self.term_os.cmd_send(f"mkidr rootfs")
        self.term_os.cmd_send(f"mount /dev/{hard_disk} ./rootfs", timeout=10)
        self.term_os.cmd_send(f"mount -o remount,noatime,nodiratime ./rootfs", timeout=10)
        self.term_os.cmd_send(f"mount -o bind /dev ./rootfs/dev", timeout=10)
        self.term_os.cmd_send(f"mount -o bind /proc ./rootfs/proc", timeout=10)
        self.term_os.cmd_send(f"mount -o bind /sys ./rootfs/sys", timeout=10)
        self.term_os.cmd_send(f"chroot ./rootfs", timeout=10)

        # 设置密码
        self.term_os.cmd_send("passwd", ret_str="New password", wait4res_str=True, timeout=30)
        self.term_os.cmd_send(f"{Term.GLB_PASSWORD}", ret_str="Retype new password", wait4res_str=True, timeout=30)
        self.term_os.cmd_send(f"{Term.GLB_PASSWORD}", timeout=30)
        self.term_os.close()


if __name__ == '__main__':
    MsgCenter(testcase_name="test01")
    reset = Reset()
    reset.init_haps()

