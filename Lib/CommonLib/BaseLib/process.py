#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/15 22:17
# @Author  : v_bkaiwang
# @File    : process.py 多进程命令调用
# @Software: win10 Tensorflow1.13.1 python3.6.3
# perf = 性能测试的性能二字


import os
import signal
import subprocess

from Lib.ComminLib.BaseLib.log_message import LOG_ERROR, LOG_WARN, LogMessage
from Lib.ComminLib.BaseLib.terminal import result_dict


class Process:
    """
    本地python 单进程/多进程执行命令 并获取结果
    cmd = 脚本
    cwd = 命令执行目录
    timeout = 超时，默认反复查询100次
    """
    def __init__(self, cwd=None, timeout=100):
        self.cwd = cwd
        self.timeout = timeout
        self.cur_cnt = 0

    @staticmethod
    def _result_check(_result):
        """
        检验返回值 返回字典格式的返回数据
        :param _result:
        :return:
        """
        exit_code, res_out = _result
        res_dict = dict()
        if int(exit_code) == 0:
            res_dict = result_dict[r'success']
        elif int(exit_code) == 1:
            res_dict = result_dict[r'excut error']
        elif int(exit_code) == 2:
            res_dict = result_dict[r'Invalid\s*Parameter']
        elif int(exit_code) == 3:
            res_dict = result_dict[r'Missing\s*Parameter']
        elif int(exit_code) == 4:
            res_dict = result_dict[r'command\s*not\s*found']
        return res_dict

    def sp_cmd_send(self, cmd=''):
        """
        执行命令 获取命令返回值
        :param cmd:
        :return:
        """
        res = subprocess.getstatusoutput(cmd)
        self.exit_code, self.res_out = res
        res_dict = self._result_check(res)
        res_dict['rettxt'] = self.res_out
        return res_dict

    def mp_cmd_send(self, cmd=''):
        # 指定目录 执行多进程命令 例如iperf3 / netperf 等
        self.mp_cmd = cmd
        self.mp = subprocess.Popen(cmd, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        self.mp_out, self.mp_err = self.mp.communicate()
        return self.mp

    def mp_result_get(self):
        # 获取self.mp命令返回值
        if self.cur_cnt >= self.timeout:
            # 超出日志输出错误 杀死进程
            LogMessage(level=LOG_WARN, module='Process', msg=f'Timeout Please check file {self.mp_cmd} ')
            try:
                os.kill(self.mp.pid, signal.SIGKILL)
            except Exception as e:
                LogMessage(level=LOG_ERROR, module='Process', msg=f'Kill Pid failed : {e} ')
            return False

        exit_code = self.mp.returncode
        if not exit_code:
            self.cur_cnt += 1
            LogMessage(level=LOG_WARN, module='Process', msg=f'cmd still running , please wait')
            return None
        elif exit_code == 0:
            return 0, self.mp_out  # 程序结束 正常返回
        else:

            LogMessage(level=LOG_ERROR, module='Process', msg=f'run %s return failed , Please Check !! stderr: %s'
                       % (self.mp_cmd, self.mp.stderr))


if __name__ == '__main__':
    sp = Process(cwd='D:')
    print(sp.sp_cmd_send('dir'))
