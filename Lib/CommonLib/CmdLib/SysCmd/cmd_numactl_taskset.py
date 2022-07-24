#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/3/4 23:37
# @Author  : v_bkaiwang
# @File    : cmd_numactl_taskset.py
# @Software: win10 Tensorflow1.13.1 python3.6.3

class CmdNumactl:
    def numactl_bindcore(self, phy_cpu_bind=None, mem_bind=None):
        """
        进行core跨Nodes测试
        :param phy_cpu_bind: 0~127
        :param mem_bind: 0~3
        :return:
        举例 phy_cpu_bind=0,mem_bind=0 表示core 0 访问node0 的内存
        """
        return '' if not phy_cpu_bind else self.__numactl(phy_cpu_bind=phy_cpu_bind, mem_bind=mem_bind)
