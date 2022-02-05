#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/4 11:53
# @Author  : v_bkaiwang
# @File    : test_case_frame.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
import allure
import traceback
from ..BaseLib.log_message import LogMessage, LOG_ERROR, LOG_INFO, LOG_SYS

# 测试结果定义
# 测试机结果定义
RET_NG = "NG"
RET_PASS = "PASS"
RET_POK = "POK"
RET_SKIP = "SKIP"


class ExceptException(Exception):
    pass


class TestCaseFrame:
    tc_result = None
    tc_name = ''
    testcase_parameter = []

    def var_create_from_conf(self, parameter: dict):
        """
        将config测试数据文件测试点转换成成员变量供使用
        {"test_point_001":"3.1415"} => self.test_point_001
        :param parameter: 字典对象
        :return:
        """
        for key, value in parameter.items():
            if isinstance(value, str):
                exec("self." + key + f"= \"{value}\"")
            else:
                exec("self." + key + f"= {value}")

    def result_check(self):
        """打印各组样本点"""
        pass_cnt = 0
        ng_cnt = 0
        for sub_tc_name, sub_tc_result in self.ret_dict.items():
            if sub_tc_result == RET_PASS:
                pass_cnt += 1
            elif sub_tc_result == RET_NG:
                ng_cnt += 1
            else:
                # 样本点用例结果不会不存在 pass ng 以外的情况 谨慎起见 报个错
                LogMessage(level=LOG_ERROR, module=self.tc_name,
                           msg=f"---------------{sub_tc_name} 执行结果异常： {sub_tc_result}-----------------")

            LogMessage(level=LOG_SYS, module=self.tc_name,
                       msg=f"---------------{sub_tc_name} 执行结果异常： {sub_tc_result}-----------------")

        # 根据样本点结果判断整体用例结果
        total_cnt = len(self.ret_dict)
        if not total_cnt:
            log_level = LOG_ERROR
            tc_result = RET_NG
            LogMessage(level=log_level, module=self.tc_name,
                       msg=f"---------------用例执行无结果：{self.tc_name}-----------------")

        elif pass_cnt == total_cnt:
            log_level = LOG_INFO
            tc_result = RET_PASS

        elif 0 < pass_cnt < total_cnt:
            log_level = LOG_ERROR
            tc_result = RET_POK
        else:
            log_level = total_cnt
            tc_result = RET_NG

        LogMessage(level=log_level, module=self.tc_name, msg=f"-------------用例执行结果：{self.tc_name}---------------")
        TestCaseFrame.tc_result = tc_result
        return tc_result

    def assert_equal(self, first, second, fails_msg=""):
        """
        用于判断各个步骤结果校验 禁止用于一般函数结果
        :param first:
        :param second:
        :param fails_msg:
        :return:
        """
        ret = True
        try:
            assert first == second, f"实际值与期望值不相等 期望{second} 实际{first}"
        except Exception as e:
            LogMessage(level=LOG_SYS, module=self.tc_name, msg=str(e))
            # 开始收集失败信息
            self.failure()
            ret = False
        return ret

    def test_frame_run(self, _step_session):
        """
        测试用例 采用与类同名 原则上一个测试py文件中一个Test类 一个测试用例 这样方便管理
        特殊情况下 一个类中多个用例
        写测试用例时 继承这个类 重写里面的方法
        :param _step_session:
        :return:
        """
        self.test_suit = _step_session  # 获得fixture 返回的 suit
        self._setup()  # 重写此方法 - 用例初始化步骤 会初始化所有配置
        self.ret_dict = dict()  # 用例集的结果

        with self.step("开始测试用例"):
            data_num = 1
            for item in self.testcase_parameter:
                self.var_create_from_conf(item)  # 将样本点中的key - value 转化成成员变量
                with self.step(f' ---------- 开始执行第 {data_num} 组样本点: {item} ------------ '):
                    try:
                        # 处理样本点异常
                        self.setup_procedure()
                        self.procedure()
                        self.teardown_procedure()
                        result = RET_PASS
                    except AssertionError as e:
                        LogMessage(level=LOG_ERROR, module=self.tc_name, msg=e)
                        result = RET_NG
                        self.failure()
                    except Exception as e:
                        stack_trace = ''.join(traceback.format_tb(e.__traceback__)).strip()
                        LogMessage(level=LOG_ERROR, module=self.tc_name, msg=stack_trace)
                        LogMessage(level=LOG_ERROR, module=self.tc_name, msg=f'{e.__class__.__name__}:{e}')
                        result = RET_NG
                        self.failure()
                    sub_tc_name = f'{self.tc_name}_sub_{data_num}'
                    self.ret_dict[sub_tc_name] = result
                    data_num += 1
        with self.step("检查用例综合结果"):
            result = self.result_check()
            assert result == RET_PASS, f"{self.tc_name} 用例结果为 : {result}"

    def step(self, msg=''):
        """
        实现 调用allure 步骤记录到report
        同时把信息记录到log
        :param msg:
        :return:
        """
        LogMessage(level=LOG_SYS, module=self.tc_name, msg=msg)
        return allure.step(msg)

    def _setup(self):
        """重写此方法 - 用例初始化步骤 会初始化所有配置"""
        pass

    def setup_procedure(self):
        """重写此方法 - 设置步骤"""
        pass

    def procedure(self):
        """重写此方法 - 用例执行步骤 这里会执行用例操作"""
        pass

    def teardown_procedure(self):
        """重写此方法 - 会执行收尾工作"""
        pass

    def teardown(self):
        """重写此方法 - 会执行收尾工作"""
        pass

    def failure(self):
        """重写此方法 - 会执行失败日志捕捉"""
        pass
