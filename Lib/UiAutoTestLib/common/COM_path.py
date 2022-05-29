import os

import yaml
Desktoppath=None
import winreg
import datetime

def yamldata_conf():
    # 读取yamlconf数据
    data = None
    loginInfo = {}
    path = os.path.join(path_YAML_FILES, "conf.yml")
    os.path.join(path_BASE_DIR, "yamlfiles")
    with open(path, encoding="utf-8") as f:
        data = yaml.load(f.read(), Loader=yaml.Loader)
    Desktoppath = data["PathData"]["Desktoppath"]
    return Desktoppath

def get_desktop():
    Dpath=yamldata_conf()
    if Dpath:
        print("桌面配置路径",Dpath)
        Desktoppath=Dpath
    else:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                              r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders',)
        Desktoppath=winreg.QueryValueEx(key, "Desktop")[0]
    print("实际桌面路径",Desktoppath)
    return Desktoppath


def mkdir(path):
    # 引入模块
    import os

    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        print(path + ' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print(path + ' 目录已存在')
        return False
# 项目的根路径
path_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 资源路径
path_resource = os.path.join(path_BASE_DIR, "resource")

# 资源图片路径
path_RESOURCE_IMAGE = os.path.join(path_BASE_DIR, "resource/IMAGE")

# yamlfiles路径
path_YAML_FILES = os.path.join(path_BASE_DIR, "yamlfiles")

# 测试用例的目录路径
path_CASE_DIR = os.path.join(path_BASE_DIR, "step/testcases")

# 配置文件目录的路径
path_CONF_DIR = os.path.join(path_BASE_DIR, "conf")

# 用例数据的项目路径
path_DATA_DIR = os.path.join(path_BASE_DIR, "casedatas")

Desktoppath=get_desktop()

# 测试结果的目录路径
# path_REPORT_DIR = os.path.join(path_BASE_DIR, "result")
path_REPORT_DIR = os.path.join(Desktoppath, "result")

# 测试报告的目录路径
path_REPORT_DIR = os.path.join(path_REPORT_DIR, "report")

# 测试报告录屏的目录路径
path_RES_DIR = os.path.join(path_REPORT_DIR, "res")

# airtest日志目录的项目路径
path_LOG_DIR = os.path.join(path_REPORT_DIR, "log")

# 自定义日志目录的项目路径
path_LOG_MY = os.path.join(path_REPORT_DIR, "report/mylog")

# 阅读截图
# path_BOOKREAD_ERROR_IMAGE = os.path.join(path_REPORT_DIR, "IMAGE")
date = datetime.date.today()
path_BOOKREAD_ERROR_IMAGE = os.path.join("D:\Read_Result", str(date))

file=os.getcwd()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mkdir(path_REPORT_DIR)#测试结果
mkdir(path_REPORT_DIR)#测试报告
mkdir(path_LOG_MY)#mylog日志
mkdir(path_LOG_DIR)#log日志
mkdir(path_resource)#资源路径
mkdir(path_RESOURCE_IMAGE)#图片资源路径
mkdir(path_RES_DIR)#测试报告录屏的目录路径
mkdir(path_BOOKREAD_ERROR_IMAGE)


