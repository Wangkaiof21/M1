#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/21 23:05
# @Author  : v_bkaiwang
# @File    : tase_case_farme.py  # 测试框架重写
# @Software: win10 Tensorflow1.13.1 python3.6.3

import allure
from ..BaseLib.log_message import LOG_ERROR, LOG_INFO, LOG_WARN, LogMessage, LOG_SYS

# 测试机结果定义
RET_NG = "NG"
RET_PASS = "PASS"
RET_POK = "POK"
RET_SKIP = "SKIP"


class TestCaseFrame:
    tc_result = None

    def init(self, testcase_name="Test_001"):
        self.case_name = testcase_name
        self.case_result = RET_PASS
        # MsgCenter(testcase_name=self.case_name)

    def var_create_from_conf(self, tc_dict):
        # 将config 测试数据文件中的测试点 转换成成员变量 供调用
        for dict_key in tc_dict.keys():
            if isinstance(dict_key[dict_key], str):
                exec("self." + dict_key + "= \"{}\"".format(tc_dict[dict_key]))
            else:
                exec("self." + dict_key + "= {}".format(tc_dict[dict_key]))

    def result_check(self):
        # 打印各组样本点的结果
        pass_cnt = 0
        ng_cnt = 0
        for sub_tc_name, sub_tc_result in self.ret_dict.items():
            if sub_tc_result == RET_PASS:
                pass_cnt += 1
            elif sub_tc_result == RET_NG:
                ng_cnt += 1
            else:
                LogMessage(level=LOG_ERROR, module=self.tc_name,
                           msg="---------------{} 执行结果异常： {}-----------------".format(sub_tc_name, sub_tc_result))
            LogMessage(level=LOG_SYS, module=self.tc_name,
                       msg="---------------{} 执行结果异常： {}-----------------".format(sub_tc_name, sub_tc_result))

            # 根据样本点结果判断整体用例结果
            total_cnt = len(self.ret_dict)
            if not total_cnt:
                log_level = LOG_ERROR
                tc_result = RET_NG
                LogMessage(level=LOG_SYS, module=self.tc_name,
                           msg="---------------用例执行无结果：{}-----------------".format(self.tc_name))
            elif pass_cnt == total_cnt:
                log_level = LOG_INFO
                tc_result = RET_PASS
            elif ng_cnt == total_cnt:
                log_level = LOG_ERROR
                tc_result = RET_NG
            elif 0 < pass_cnt < total_cnt:
                log_level = LOG_ERROR
                tc_result = RET_POK
            else:
                pass
            LogMessage(level=LOG_SYS, module=self.tc_name,
                       msg="---------------用例执行结果：{}-----------------".format(self.tc_result))
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
            assert first == second, "实际值与期望值不相等 期望{} 实际{}".format(second, first)
        except Exception as e:
            LogMessage(level=LOG_SYS, module=self.tc_name,
                       msg=str(e))
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
            LogMessage(level=LOG_SYS, module=self.tc_name,
                       msg=f"-----------------------testcase_parameter 参数为 {self.testcase_parameter}")
            # 遍历样本点 需要提前调用方法set_test_case_parameter 将样本点设置进用例！！！
            for item in self.testcase_parameter:
                self.var_create_from_conf(item)  # 将样本点中的key-value 转化成 成员变量
                sub_tc_name = self.tc_name + "_sub_%s" % str(data_num)  # 用例集的名称
                with self.step(f'-----------开始执行 {data_num} 样本点。测试点 {self.test_point} -------------'):
                    data_num = data_num + 1
                    try:  # 处理样本点测试异常
                        self.setup_procedure()  # 重写此方法 - 设置步骤
                        self.procedure()  # 重写此方法 - 用例执行步骤 这里会执行用例操作
                        result = RET_PASS
                    except AssertionError as e:
                        LogMessage(level=LOG_ERROR, module=self.tc_name, msg=e)
                        result = RET_NG
                        self.failure()  # 重写此方法 - 会执行失败日志捕捉
                    try:  # 捕捉样本点 teardown 异常
                        self.teardown_procedure()  # 重写此方法 - 会执行收尾工作
                    except:
                        result = RET_NG
                    self.ret_dict[sub_tc_name] = result
                LogMessage(level=LOG_ERROR, module=self.tc_name, msg="")

        with self.step('检查用例综合结果'):
            result = self.result_check()
            assert result == RET_PASS, f'{self.tc_name} 用例结果为 {result}'

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
