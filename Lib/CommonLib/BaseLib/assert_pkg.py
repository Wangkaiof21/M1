#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/3/6 12:01
# @Author  : v_bkaiwang
# @File    : assert_pkg.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
from typing import Iterable
# from .log_message import LogMessage, LOG_ERROR, LOG_INFO
from Lib.CommonLib.BaseLib.log_message import LogMessage, LOG_ERROR, LOG_INFO
from Lib.CommonLib.CoreLib.msg_center import MsgCenter
import os

FILE_NAME = os.path.split(__file__)[-1]
MsgCenter(testcase_name=FILE_NAME)


def assert_in(expect, result) -> bool:
    """
    判断预期值是否在结果里
    :param expect:期望值
    :param result:结果
    :return:bool
    """
    # except 是意料之外 expect 是预测
    ret = False
    if isinstance(result, dict):
        expect_set = set(expect.items())
        result_set = set(result.items())
        # .issubset() 判断集合 x 的所有元素是否都包含在集合 y 中：
        ret = expect_set.issubset(result_set)
    elif isinstance(result, Iterable) and not isinstance(result, str):
        expect_set = set(expect)
        result_set = set(result)
        ret = expect_set.issubset(result_set)
    else:
        LogMessage(level=LOG_ERROR, module=FILE_NAME,
                   msg=f"Assert_in result type_error .Only dict,list,set,or tuple are supported")
    LogMessage(level=LOG_INFO, module=FILE_NAME, msg=f"Compare with {expect} and {result}")

    return ret


def assert_equal_deviation(real_val, expect, deviation=0.05):
    """
    带偏差判定 即second * (1-deviation)<first(second * (1-deviation)) 范围内 返回正常
    :param real_val: 检测值 支持整数浮点
    :param expect: 期望值
    :param deviation: 偏差值 浮点
    :return:
    """
    ret = True
    f_val = float(real_val)
    s_val = float(expect)
    s_val_max = s_val * (1 + deviation)
    s_val_min = s_val * (1 - deviation)
    try:
        assert s_val_min <= f_val <= s_val_max, f"期望值与实际值不等 ,实际={real_val} ,期望={expect},偏差={deviation}"
    except Exception as e:
        LogMessage(level=LOG_ERROR, module="assert_equal_deviation",
                   msg=f"Assert_in result type_error .Only dict,list,set,or tuple are supported {e}")
        ret = False
    return ret


def assert_greater_equal(real_val, expect, deviation=0.05):
    """
    带偏差判定 即second * (1-deviation)<=first 范围内 返回正常
    :param real_val: 检测值 支持整数浮点
    :param expect: 期望值
    :param deviation: 偏差值 浮点
    :return:
    """
    ret = True
    f_val = float(real_val)
    s_val = float(expect)
    s_val_min = s_val * (1 - deviation)
    try:
        assert f_val >= s_val_min, f"期望值与实际值不等 ,实际={real_val} ,期望={expect},下偏差={deviation}"
    except Exception as e:
        LogMessage(level=LOG_ERROR, module="assert_greater_equal",
                   msg=f"Assert_in result type_error .Only dict,list,set,or tuple are supported {e}")
        ret = False
    return ret


def assert_less_equal(real_val, expect, deviation=0.05):
    """
    带偏差判定 first <= second * (1-deviation) 范围内 返回正常
    :param real_val: 检测值 支持整数浮点
    :param expect: 期望值
    :param deviation: 偏差值 浮点
    :return:
    """
    ret = True
    f_val = float(real_val)
    s_val = float(expect)
    s_val_max = s_val * (1 + deviation)
    try:
        assert f_val <= s_val_max, f"期望值与实际值不等 ,实际={real_val} ,期望={expect},偏差={deviation}"
    except Exception as e:
        LogMessage(level=LOG_ERROR, module="assert_less_equal",
                   msg=f"Assert_in result type_error .Only dict,list,set,or tuple are supported {e}")
        ret = False
    return ret


# def test_(ll=1, vv=2):
#     c = ll * vv
#     LogMessage(level=LOG_ERROR, module="test", msg=f"result = {c}")
#     return
#
#
# if __name__ == '__main__':
#     test_()

if __name__ == '__main__':
    expect_dict = {1: 11, 2: 22}
    result_dict = {1: 11, 2: 22, 3: 33}
    print(assert_in(expect_dict, result_dict))
    print(assert_in("123", "1324"))
    print(assert_in((1, 2, 3), {1, 2, 3, 4}))
