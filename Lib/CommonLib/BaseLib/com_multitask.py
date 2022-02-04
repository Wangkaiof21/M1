#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/16 18:16
# @Author  : v_bkaiwang
# @File    : com_multitask.py 多任务发命令 取回返回值
# @Software: win10 Tensorflow1.13.1 python3.6.3

import time

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from .process import Process
from .terminal import Terminal
from .log_message import LogMessage, LOG_ERROR


def multitask_cmd(cmd_iter, term, max_worker=None, chunk_size=1, timeout=5):
    """
    多进程执行cmd命令 并取回返回值
    :param cmd_iter: 可迭代的cmd 操作集 （list tuple set）
    :param term: Process对象
    :param max_worker: 进程数
    :param chunk_size: 指cmd_iter分片大小 每个进程的任务量
    :param timeout:超时时间
    :return:返回生成器
    """
    if isinstance(term, Terminal):
        # 多线程执行任务
        with ThreadPoolExecutor(max_worker=max_worker) as executor:
            result = executor.map(term.cmd_send, cmd_iter, timeout=timeout, chunksize=chunk_size)

    # 本地执行cmd
    elif isinstance(term, Process):
        # 由于sp_cmd 使用的时subprocess 这里需要多进程实现多任务
        with ProcessPoolExecutor(max_worker=max_worker) as executor:
            result = executor.map(term.sp_cmd_send, cmd_iter, timeout=timeout, chunksize=chunk_size)
    else:

        LogMessage(level=LOG_ERROR, module=multitask_cmd.__name__,
                   msg="term{} 应该传入 Terminal/Process" .format(term))

    return result


def multitask(task, args, max_worker=None, chunk_size=1, timeout=5, by_thread=True):
    """
    多任务执行task 取回返回值 使用一个terminal对象 同时执行命令
    :param task: 任务函数名
    :param args: 可迭代的cmd 操作集 （list tuple set）
    :param max_worker: 进程数
    :param chunk_size: 指cmd_iter分片大小 每个进程的任务量
    :param timeout:
    :param by_thread: 默认多线程
    :return:
    """
    if by_thread:
        with ThreadPoolExecutor(max_worker=max_worker) as executor:
            result = executor.map(task, args, timeout=timeout, chunksize=chunk_size)
    else:
        with ProcessPoolExecutor(max_worker=max_worker) as executor:
            result = executor.map(task, args, timeout=timeout, chunksize=chunk_size)
    return result


if __name__ == '__main__':
    st = time.perf_counter()
    # 本地执行
    res1 = list(multitask_cmd(['whoami', 'echo "hello"'], term=Process()))
    for sub_result in res1:
        print(sub_result['rettxt'])
    ed = time.perf_counter()
    print(ed - st)

    print("------------------------------------------------------------------------------------------")

    st = time.perf_counter()
    # 远端执行
    term1 = Terminal(host_ip="Term.GLB_HOST", port=22, username='root', password="Term.GLB_PASSWORD")
    term1.connect()
    res1 = multitask_cmd(['cd /home/gwl', 'pwd'], term=term1)
    for sub_result in res1:
        print(sub_result['rettxt'])
    ed = time.perf_counter()
    print(ed - st)
