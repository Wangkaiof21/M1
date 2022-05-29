import os
from airtest.cli.parser import cli_setup
from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco

from Lib.UiAutoTestLib.date.Chapters_data import MyData
from Lib.UiAutoTestLib.common.COM_path import path_BASE_DIR, path_LOG_DIR

from Lib.CommonLib.BaseLib.log_message import LogMessage, LOG_ERROR, LOG_INFO, LOG_DEBUG
from Lib.CommonLib.CoreLib.msg_center import MsgCenter

FILE_NAME = os.path.split(__file__)[-1]
MsgCenter(logger_name=FILE_NAME, level=LOG_DEBUG)


class CommonDevices:
    def __init__(self):
        if not G.DEVICE:
            self.adb_path = os.path.join(path_BASE_DIR, MyData.UserPath_dir["adbpath"])
            if not cli_setup():
                self.connect_devices()
                if MyData.DeviceData_dir["androidpoco"] is None:
                    MyData.DeviceData_dir["androidpoco"] = AndroidUiautomationPoco()
                    LogMessage(module=FILE_NAME, level=LOG_INFO,
                               msg="完成android原生元素定位方法初始化【{}】".format(MyData.DeviceData_dir["androidpoco"]))

    def connect_devices(self):
        conf = MyData.EnvData_dir["device"] + "://" + MyData.EnvData_dir["ADBip"] + "/" + MyData.EnvData_dir[
            "ADBdevice"]
        LogMessage(module=FILE_NAME, level=LOG_INFO, msg=f"尝试连接配置的adb {conf}")
        method = MyData.EnvData_dir["method"]
        try:
            if "127" in MyData.EnvData_dir["ADBdevice"]:
                method = MyData.EnvData_dir["simulator"]
            auto_setup(__file__, logdir=path_LOG_DIR, devices=[conf + method, ], project_root=path_BASE_DIR)
        except Exception as e:
            LogMessage(module=FILE_NAME, level=LOG_INFO, msg=f"尝试查看电脑连接的可用移动设备 {e}")
            self.adb_dispose()
            MyData.EnvData_dir["ADBip"] = "127.0.0.1:5037"
            conf = MyData.EnvData_dir["device"] + "://" + MyData.EnvData_dir["ADBip"] + "/" + \
                   MyData.EnvData_dir["ADBdevice"]
            LogMessage(level=LOG_INFO, msg=f"conf{conf}")
            method = MyData.EnvData_dir["method"]
            auto_setup(__file__, logdir=path_LOG_DIR, devices=[conf + method, ], project_root=path_BASE_DIR)
            LogMessage(module=FILE_NAME, level=LOG_INFO, msg=f"连接成功")
            return True

    def adb_dispose(self):
        """初始化"""
        index = 10
        while index >= 0:
            index = index - 1
            try:
                LogMessage(module=FILE_NAME, level=LOG_INFO, msg=f"adb_path: {self.adb_path}")
                cmd_result = os.popen(self.adb_path + ' devices')
                devlist = cmd_result.readlines()
                for line in range(1, len(devlist)):
                    if "device" in devlist[line]:
                        result = devlist[line].split("	device")
                        MyData.EnvData_dir["ADBdevice"] = result[0]
                        print("连接adb可用列表中", MyData.EnvData_dir["ADBdevice"])
                        return True
                raise
            except Exception as e:
                sleep(8)
                LogMessage(module=FILE_NAME, level=LOG_ERROR, msg=f"查询设备信息异常=>{e}")

    @staticmethod
    def get_dev_info():
        devlist = []
        cmd = os.popen('adb devices')
        list_ = cmd.readlines()
        for i in range(len(list)):
            if list_[i].find('\tdevice') != -1:
                temp = list_[i].split('\t')
                devlist.append(temp[0])
        return devlist

    def check_connect_ability(self, flag=0):
        '''
        flag =0时，当连接正常时返回True(default)
        flag!=0时，直接打印出结果
        '''
        warring = '''ADB连接失败, 请check以下项:
        1. 是否有连接上手机？请连接上手机选并重新check连接性!
        2. 是否有开启"开发者选项\\USB调试模式"?\n'''
        connect_info = self.get_dev_info()
        if len(connect_info) == 0:
            return False
        if len(connect_info) == 1:
            if flag != 0:
                print('连接正常')
                print(f'设备SN: {connect_info[0]}')
            else:
                return True
        if len(connect_info) >= 2:
            print('连接正常，当前有连接多台设备. ')
            for i in range(len(connect_info)):
                print(f'设备{i + 1} SN: {connect_info[i]}')
            return True
