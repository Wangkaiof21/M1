#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/3/4 23:35
# @Author  : v_bkaiwang
# @File    : cmd_devmem.py 寄存器读写
# @Software: win10 Tensorflow1.13.1 python3.6.3

import re
from ...log_message import LogMessage, LOG_INFO, LOG_ERROR
from ...terminal import Terminal


class DevMem:
    def __init__(self, terminal=None):
        self.terminal = terminal if isinstance(terminal, Terminal) else LogMessage(level=LOG_ERROR, msg="DevMem")

    def devmem_read(self, address, chip_id=0, die_id=0):
        """
        底层寄存器读取命令
        :param address:
        :param chip_id:
        :param die_id:
        :return:
        """
        result = 0
        if self.terminal.is_uefi_view() or self.terminal.is_mcp_view() or self.terminal.is_scp_view():
            cmd = "mm {}".format(address)
            re_str = r'MEM.*:\s*(\W+)'
            ret_cmd = self.terminal.cmd_send(cmd=cmd, ret_str='>')
            # 输入q命令才能正常退出
            self.terminal.cmd_send(cmd="q")
            if ret_cmd['recode'] == 0:
                # 正则获取寄存器的值
                ret_re = re.findall(re_str, ret_cmd['rettxt'])
                if len(ret_re) > 0:
                    result = int(ret_re[0], 16)
        else:
            cmd = "mm {}".format(address)
            re_str = r'Value\s*at\s*address\s*.*\s*(\W+)'
            ret_cmd = self.terminal.cmd_send(cmd=cmd, ret_str='>')
            if ret_cmd['recode'] == 0:
                # 直接响应寄存器的值
                result = int(ret_cmd['rettxt'])
        return result

    def devmem_write(self, address, wdata, chip_id=0, die_id=0):
        """
        底层寄存器写入命令
        :param address: 地址
        :param wdata: 写入的值
        :param chip_id:
        :param die_id:
        :return:
        """
        if self.terminal.is_uefi_view() or self.terminal.is_mcp_view() or self.terminal.is_scp_view():
            cmd = "mm {} {}".format(address, wdata)
        else:
            cmd = "devmem {} w {}".format(address, wdata)
        self.terminal.cmd_send(cmd=cmd)

    def arm_sys_reg_read(self, reg_name, core_id=0, chip_id=0, die_id=0):
        """
        底层寄存器读取命令
        :param reg_name: 寄存器名称
        :param core_id: 处理器编号
        :param chip_id:
        :param die_id:
        :return:
        """
        result = 0
        cmd = 'rdasr -p{} -r{}'.format(core_id, reg_name)
        ret_cmd = self.terminal.cmd_send(cmd)
        if ret_cmd['recode'] == 0:
            # 正则获取寄存器的值
            ret_re = re.findall(r'(0x[1-9a-fA-F])+', ret_cmd['rettxt'])
            if len(ret_re) > 0:
                result = int(ret_re[0], 16)
        return result

    def arm_sys_reg_write(self, reg_name, wdata, core_id=0, chip_id=0, die_id=0):
        """
        底层寄存器写入命令
        :param reg_name: 寄存器名称
        :param core_id: 处理器编号
        :param chip_id:
        :param die_id:
        :return:
        """
        cmd = 'wrasr -p{} -r {} {}'.format(core_id, reg_name, wdata)
        self.terminal.cmd_send(cmd)

    def apb_reg_read(self, address, chip_id, die_id):
        """

        :param address:
        :param chip_id:
        :param die_id:
        :return:
        """
        cmd = 'echo regread {} {} {} > regrw'.format(chip_id, die_id, address)
        result = self.terminal.cmd_send(cmd)
        return result

    # ECAM 寄存器读写命令
    def ecam_reg_read(self, address, chip_id=0, die_id=0):
        """

        :param address:
        :param chip_id:
        :param die_id:
        :return:
        """
        cmd = 'echo ecamread {}:{} {} > regrw'.format(chip_id, die_id, address)
        result = self.terminal.cmd_send(cmd)
        return result

    def ecam_reg_write(self, address, wdata,chip_id=0, die_id=0):
        """

        :param address:
        :param chip_id:
        :param die_id:
        :return:
        """
        cmd = 'echo ecamread {}:{}:{} {} > regrw'.format(chip_id, die_id, address, wdata)
        result = self.terminal.cmd_send(cmd)
        return result

    # itos 寄存器读写命令
    def itos_reg_read(self, pe_idx, address, bit=32, safe_mode=False) -> str:
        """

        :param pe_idx: pe 索引
        :param address: 地址
        :param bit:位数
        :param safe_mode:
        :return:
        """
        cmd = 'itosrun -tr' if safe_mode else 'itosrun -ur'
        cmd += f'{pe_idx} {address} {bit}'
        if safe_mode:
            result = self.terminal.cmd_send(cmd, ret_str='Success', delay_recv=5)['rettxt']
        else:
            result = self.terminal.cmd_send(cmd, ret_str='Exception', delay_recv=5)['rettxt']
            if not isinstance(result, bool):
                try:
                    result = re.findall(r'read:\s(0x.*)', result[0].strip())
                except IndexError:
                    LogMessage(LOG_ERROR, 'c,d-devmem', f'{"*" * 20} {result}')
        return result

    def itos_reg_write(self, pe_idx, address, hex_value, bit=32, safe_mode=False) -> str:
        """

        :param pe_idx: pe 索引
        :param address: 地址
        :param bit:位数
        :param safe_mode:
        :return:
        """
        cmd = 'itosrun -tw' if safe_mode else 'itosrun -uw'
        cmd += f'{pe_idx} {address} {hex_value} {bit}'
        if safe_mode:
            result = self.terminal.cmd_send(cmd, ret_str='Success', delay_recv=5)['rettxt']
        else:
            result = self.terminal.cmd_send(cmd, ret_str='Exception', delay_recv=5)['rettxt']
            if not isinstance(result['rettxt'], bool):
                try:
                    tmp = re.findall(r'read:\s(0x.*)', result[0].strip())
                    result['rettxt'] = tmp
                except IndexError:
                    LogMessage(LOG_ERROR, 'c,d-devmem', f'{"*" * 20} {result}')
        return result


if __name__ == '__main__':

    LogMessage(level=LOG_INFO, module="Mysql", msg=" check {}".format(">>>>>>>"))
    term = Terminal(host_type='telnet', host_ip='196.168.3.100', port=10003, proxy=True, view_mode='uefi')
    term.connect()
    devmem = DevMem(term)
    res = devmem.itos_reg_read(1, '0x2B2000F0', safe_mode=False)
    devmem.itos_reg_write(1, '0x2B2000F0', '0xf', safe_mode=False)
    res = devmem.itos_reg_read(1, '0x2B2000F0', safe_mode=False)
    print(res)



