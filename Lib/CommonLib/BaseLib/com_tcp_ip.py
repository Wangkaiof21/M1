#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/5 18:12
# @Author  : v_bkaiwang
# @File    : com_tcp_ip.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
# tcp/ip相关函数
import re

IPV4_REG_EX = r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$'
IPV6_REG_EX = r'^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:)' \
              r'{6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[' \
              r'0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4})' \
              r'{1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))' \
              r'{3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})' \
              r'?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))' \
              r'|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:(' \
              r'(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(' \
              r'([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]' \
              r'|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:)' \
              r'{1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)' \
              r'(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4})' \
              r'{0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$  '


def ipv4_check(ip):
    """
    检查ipv4是否合法
    :param ip:
    :return:
    """
    pattern = re.compile(IPV4_REG_EX)
    return True if pattern.search(ip) else False


def ipv6_check(ip):
    """
    检查ipv6是否合法
    :param ip:
    :return:
    """
    if '/' in ip:
        ip, mask = ip.split('/')
    pattern = re.compile(IPV6_REG_EX)
    return True if pattern.search(ip) else False


def ip_check(ip, ip_version='IPV4'):
    """
    检查ipv6是否合法
    :param ip: 字符串
    :param ip_version: ip 版本
    :return:
    """
    return ipv4_check(ip) if ip_version == 'IPV4' else ipv6_check(ip)
