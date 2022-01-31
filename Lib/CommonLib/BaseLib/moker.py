#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/16 18:17
# @Author  : v_bkaiwang
# @File    : moker.py
# @Software: win10 Tensorflow1.13.1 python3.6.3

from functools import wraps


class Mock:
    def __init__(self, feedback=None):
        self.feedback = feedback

    def __call__(self,func):
        @wraps(func)
        def mock_func(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(e)
            return self.feedback
        return mock_func


mock = Mock

if __name__ == '__main__':
    @mock(12)
    def add_(a, b):
        return a + b
    print(add_(3, 4))

