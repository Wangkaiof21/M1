#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/3/21 13:55
# @Author  : v_bkaiwang
# @File    : zentao.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
import json
import sys
import os
import datetime

from .mysql import Mysql
a = sys.path.append((os.path.dirname((os.path.abspath('__file__')))).split("Lib")[0])


class ReloadResult:
    def __init__(self):
        self.file_path = (os.path.dirname((os.path.abspath("__file__")))).split("Lib")[0]
        self.template_path = os.path.join(self.file_path, "TestLog", "result.xlsx")
        path = os.path.join((os.path.join("allure-report", "data")), "test-cases")
        self.json_path = os.path.join(self.file_path, path)

    def file_names(self):
        file_path = self.json_path
        file_list = os.listdir(file_path)
        return file_list

    # 读取json数据
    def parsing_json(self, path_name):
        """

        :param path_name:
        :return: case_list: 用例样本点执行结果
                 step_list: 样本点步骤执行结果
                 log_url: 报告链接
                 start_time: 用例开始执行时间
        """
        # 用例样本执行结果
        case_list = []
        # 样本点步骤及执行结果
        step_list = []
        with open(path_name, 'rb') as jsonfile:
            json_string = json.load(jsonfile)

        # 获取用例名及其执行结果
        dict_caseinfo = {}
        casename = (json_string["description"])
        start_time = json_string["time"]['start']
        status = json_string["status"]
        dict_caseinfo["case_name"] = casename + ":" + status
        case_list.append(dict_caseinfo)
        # 获取log_url
        try:
            log_url = (json_string["extra"]["history"]["items"][0])["reportUrl"]
            history_url = (json_string["extra"]["history"]["items"][1])["reportUrl"]
        except Exception as e:
            log_url = None
            print(e)

        if status != "skeped":
            # 获取用例样本点详细步骤及其执行结果
            step_name = json_string["testStage"]["steps"]
            for i in range(len(step_name)):
                if step_name[i]["name"] == "开始执行用例":
                    ret = step_name[i]["steps"]
            sample_list = []
            dict_sample = {}
            for all_data in ret:
                list_steps = {}
                dict_steps = {}
                index = 0
                for par_data in all_data["steps"]:
                    list_steps[par_data["name"]] = par_data["status"]
                    if par_data["status"] == "failed":
                        index += 1
                    dict_steps[((all_data["name"]).replace("_", "").replace("开始执行", "")).split(":")[0]] = list_steps
                if index != 0:
                    sample_list.append((all_data["name"]).replace("_", "").replace("开始执行", "") + ":" + "fail")
                else:
                    sample_list.append((all_data["name"]).replace("_", "").replace("开始执行", "") + ":" + "pass")
                step_list.append(dict_steps)
                dict_sample["sample_name"] = sample_list
            case_list.append(dict_sample)
        return case_list, step_list, log_url, start_time

    # 数据回写mysql
    def sql_write(self, case_name, result, status, log_url, start_time):
        """

        :param case_name: 用例名
        :param result: 用例结果
        :param status: 用例执行状态
        :param log_url: 用例log链接
        :param start_time: 用例开始执行时间
        :return:
        """
        mysql = Mysql()
        """
        系要提前获取的值
        1 版本信息、环境信息 M1 和 M1-FT 和 M+HAPS-B010
        2 用例名 MTEST_0010
        """
        product_name = "ARM"
        project_name = "M1-FT-ES"
        build_name = "HAPS-B020"

        # zt_product表
        product = mysql.query(tb_name="zt_product", fields="id", condition=f"name'{product_name}'")
        product = product[0]['id']

        # zt_project表
        project = mysql.query(tb_name="zt_project", fields="id", condition=f"name'{project_name}'")
        project = project[0]['id']

        # zt_build表 通过product和project确定
        build = mysql.query(tb_name="zt_build", fields="id",
                            condition=f"name'{build_name}' and product={product} and project={project}")
        build = build[0]['id']

        # zt_testtask表 通过product和project, build确定
        testtask = mysql.query(tb_name="zt_testtask", fields="id",
                               condition=f"name='M+H_B020_PCIe' and product={product} "
                               f"and project={project} and build={build}")
        testtask = testtask[0]['id']

        # zt_case表 通过product\用例名（testcase）确定
        try:

            testcase = mysql.query(tb_name="zt_case", fields="id", condition=f"testcaseid='{case_name}' "
                                   f"and product={product}")
            testcase = testcase[0]["id"]

            version = mysql.query(tb_name="zt_case", fields="storyVersion", condition=f"testcaseid='{case_name}' "
                                  f"and product={product}")
            version = version[0]["storyversion"]

            # zt_testrun 通过 testtask testcase version确定
            testrun = mysql.query(tb_name="zt_testrun", fields="id", condition=f"task='{testtask}' "
                                  f"and `case`={testcase} and version {version}")
            testrun = testrun[0]["id"]

            # testrun数据更新 lastRunResult update方式(pass/fail填done,blocked填blocked填)
            # TODO 更新当前用例结果、状态
            ret = mysql.update(tb_name="zt_testrun", update_field=f"lastRunResult='{result}', status='{status}'",
                                condition=f'id={testrun}')
            if ret:
                print("zt_testrun 表 更新成功")
            # zt_testresult数据更新 testcase\testrun\version insert方式
            # TODO job\compile\duration 写0 stepResult 写空 xml写空
            field = "(run `case`,version,job,compile,caseResult,stepResults,lastRunner,date,duration,xml,logurl)"
            value = f"({testrun},{testcase},{version},0,0'fail','','jenkins','{start_time},0,0,'','{log_url}')"
            ret = mysql.raw_sql(f"insert into zt_testresult {field} values{value};")

            if ret:
                print("zt_testrun 表 插入成功")
            # zt_testresultdetail 数据更新 product\project\build\testtask\testcase\testrun\testresult
            field = "(product,project,build,`case`,testtask,testrun,testresult,tp_id,tp_desc,step_id,step_desc,"\
                    "result,result_desc,duration)"
            value = f"({product},{project},{build},{testcase},{testrun}, 1, 1, 1, 'jenkins', 1, 'xx', 'pass'," \
                    f"'desc, '30')"
            ret = mysql.raw_sql(f"insert into zt_testresultdetail {field} value{value}")

        except Exception as e:
            print(e, f"未在数据库检索到用例名：{case_name}")

    # 写入禅道数据库
    def run(self):
        # 获取所有json文件
        file_list = self.file_names()
        # 遍历循环读取
        for file in file_list:
            case_list, step_list, log_url, start_time = self.parsing_json(os.path.join(self.json_path, file))
            # 循环写入禅道 格式处理
            case_name = (case_list[0]['case_name'].split(":")[0])
            result = (case_list[0]['case_name'].split(":")[1][:4])  # 处理成pass fail
            # 对应关系 pass/fail(done) blocked(blocked)
            if result == "pass" or result == 'fail':
                status = "done"
            else:
                status = "blocked"

            start_time = datetime.datetime.fromtimestamp(int(str(start_time)[:-3]))
            # 写入禅道数据库
            read_json.sql_write(case_name, result, status, log_url, start_time)


if __name__ == '__main__':
    read_json = ReloadResult()
    read_json.run()
