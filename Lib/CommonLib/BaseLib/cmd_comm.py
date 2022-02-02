#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/14 19:30
# @Author  : v_bkaiwang
# @File    : cmd_comm.py
# @Software: win10 Tensorflow1.13.1 python3.6.3


import os

from .terminal import Terminal
from .log_message import LogMessage, LOG_INFO, LOG_ERROR


class FileOperation:
    @staticmethod
    def file_is_exist(terminal, filepath):
        # 在指定目录查看文件是否存在
        cmd = 'find %s' % filepath
        if not isinstance(terminal, filepath):
            return False
        ret_dict = terminal.cmd_send(cmd)
        if ret_dict.get('retcode') == 0 and 'No such file or directory' not in ret_dict.get('rettxt'):
            return True
        else:
            LogMessage(level=LOG_ERROR, module='FileOperation', msg=f"file_is_exist, is not existed {filepath}")
            return False

    @staticmethod
    def touch_file(terminal, filepath):
        """
        新建指定文件
        :param terminal:
        :param filepath:
        :return:
        """
        cmd = 'touch {}'.format(filepath)
        ret_dict = terminal.cmd_send(cmd)
        if ret_dict.get('retcode') == 0:
            return True
        else:
            return False

    @staticmethod
    def rm_file(terminal, filepath):
        """
        删除文件
        :param terminal:
        :param filepath:
        :return:
        """
        rm_cmd = f'echo {os.getenv("PASSWD")} | sudo -S rm -rf {filepath}'
        ret_dict = terminal.cmd_send(rm_cmd)
        if ret_dict.get('retcode') == 0:
            return True
        else:
            return False

    @staticmethod
    def user_env_access(terminal, filepath):
        """
        模拟多用户访问一台机器，文件锁操作，在指定机器检查filepath是否存在
        存在返回失败，表明有人占用，不能访问，不存在则新建文件‘new_file’标明可访问机器
        :param terminal: 
        :param filepath: 
        :return: 
        """
        flie_list = filepath.split(r'/')
        user = flie_list[-1].replace('.txt', '').replace('user_', '')
        flie_list[-1] = 'user*'
        old_file = r'/'.join(flie_list)
        fine_cmd = 'find {}'.format(old_file)
        touch_cmd = 'touch {}'.format(old_file)
        ret_dict = terminal.cmd_send(fine_cmd, ret_str="")
        # 存在则返回失败
        if ret_dict.get('retcode') == 0 and 'No such file or directory' not in ret_dict.get('rettxt'):
            LogMessage(level=LOG_ERROR, module='FileOperation', msg=f"file lock: {filepath}, The env is used ,Please "
                       f"wait user:{user}")
            return False
        else:
            LogMessage(level=LOG_ERROR, module='FileOperation', msg=f"file lock, The env not used , Welcome")
            terminal.cmd_send(touch_cmd)
            return True
        
    @staticmethod
    def user_env_close(terminal, filepath):
        """
        访问结束 将新建的文件path删除
        :param terminal: 
        :param filepath: 
        :return: 
        """
        del_cmd = 'rm -rf{}'.format(filepath)
        terminal.cmd_send(del_cmd)


def rebot(terminal):
    """
    重启
    :param terminal: 
    :return: 
    """
    if not isinstance(terminal, Terminal):
        return False
    cmd_result = terminal.cmd_send(cmd='sudo rebot')
    return cmd_result


def pid_kill_cmd(process_, all=False):
    """
    linux杀进程
    :param process_: 进程号
    :param all: 是否要杀掉（进程名）
    :return: 杀进程命令
    """
    passwd = os.getenv('PASSWD')
    if all:
        return f'echo {passwd} | sudo -S killall -9 {process_}'
    else:
        return f'echo {passwd} | sudo -S kill -s -9 {process_}'if process_.isdigit() else f'process_' \
            f'pid=`pidof{process_}`;[[ $process_pid -ne 0 ]] && kill -s 9 $$process_pid'


if __name__ == '__main__':
    from Lib.FeatureLib.PerfLib.perf_config import PerfTermCfg as Term
    term = Terminal(host_type=Term.GLB_HOST_TYPE, host_ip=Term.GLB_HOST, port=Term.GLB_PORT,
                   username=Term.GLB_USER, password=Term.GLB_PASSWORD, timeout=100,
                   hold=True)
    term.connect()
    filepath = Term.FILE_LOCK
    FileOperation.user_env_access(term, filepath)
    FileOperation.user_env_close(term, filepath)
