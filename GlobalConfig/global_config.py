#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/6 11:56
# @Author  : v_bkaiwang
# @File    : global_config.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
# 自动化工厂相关
import os
import json

ENVS = {}
ENV_INDEX = 123
ENV = ENVS.get(ENV_INDEX)
PROXY_SZ = {
    'host_type': 'ssh',
    'host_ip': '30.18.9.101',
    'port': 22,
    'username': 'mtest',
    'password': 'mtest',

}
PROXY_DG = {
    'host_type': 'ssh',
    'host_ip': '183.233.222.243',
    # 'host_ip': '183.233.222.244',
    'port': 22456,
    'username': 'mtest',
    'password': 'mtest',

}
ENVS_ = json.load(open(os.path.join(os.path.dirname(__file__), 'evbs_info.json'), 'r'))
ENV_NAME_ = 'ENV_132_HAPS_TELNET'
ENV_ = ENVS.get(ENV_NAME_)
PROXY_ = PROXY_SZ if ENV_['host_ip'][:7] == '192.168' else PROXY_DG
SERVER_TYPE = 'fg'
