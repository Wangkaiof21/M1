from functools import wraps
from time import perf_counter, sleep
import re
import argparse

from airtest.aircv import aircv
from airtest.core.api import *

from common.COM_devices import CommonDevices
from common.COM_nude import Nude
from common.COM_path import *
from common.COM_path import *
import yaml
import types
from airtest.core.android.recorder import *

# from common.COM_data import MyData
spendtime = None

def mysnapshot(loc_desc,IMG_parameter,quality=None,max_size=None):
    # 0, 160, 1067, 551
    filename = loc_desc + ".png"
    file_path = os.path.join(path_RESOURCE_IMAGE, filename)
    if not ST.LOG_DIR or not ST.SAVE_IMAGE:
        return
    if not quality:
        quality = ST.SNAPSHOT_QUALITY
    if not max_size:
        max_size = ST.IMAGE_MAXSIZE
    screen = G.DEVICE.snapshot()
    screen = aircv.crop_image(screen, IMG_parameter)
    aircv.imwrite(file_path, screen, quality, max_size=max_size)

    try_log_screen(screen)
    # tempalte = Template(
    #     r"C:\Users\admin\AppData\Local\Temp\AirtestIDE\scripts\e54a0377105932d86d3b89f24ad95d13\1616493784313.jpg")
    # print(tempalte)
    # pos = tempalte.match_in(screen)




def myscreenshot(file_path,loc_desc):
    # date_decs = time.strftime("%Y-%m-%d_%H_%M_%S")
    filename = str(loc_desc) + ".png"
    file_path = os.path.join(file_path, filename)
    try:
        snapshot(filename=file_path, msg=loc_desc)
    except Exception as e:
        print(e)

def screenshot(loc_desc):
    date_decs = time.strftime("%Y-%m-%d_%H_%M_%S")
    filename = date_decs + loc_desc + ".png"
    file_path = os.path.join("ERROR_IMAGE", filename)
    try:
        # 获取当前时间，并转换为指定格式的字符串
        date_decs = time.strftime("%Y-%m-%d_%H_%M_%S")
        filename = date_decs + loc_desc + ".png"
        print(filename)
        file_path = os.path.join("D://ERROR_IMAGE/", filename)
        print(file_path)
        snapshot(filename=file_path, msg=loc_desc)
    except Exception as e:
        print(e)
        raise e

def PosTurn(pos):  # 坐标转化
    width = G.DEVICE.display_info['width']
    height = G.DEVICE.display_info['height']
    POS = [pos[0] * width, pos[1] * height]
    return POS


def read_yaml(filepath):
    with open(filepath, encoding='utf-8') as file:
        value = yaml.safe_load(file)
    return value


def clock(type=None):  # 计时器
    """stop结束返回时间"""
    global start_time
    if type == "stop":
        spendtime = '%.2f' % (perf_counter() - start_time)
        print("花费时间{}秒:".format(spendtime))
        return spendtime
    else:
        start_time = perf_counter()


def start_record(maxtime=3600):
    """录屏功能，start,stop"""
    G.DEVICE.start_recording(max_time=maxtime)
    # print(MyData.EnvData_dir)
    # Recorder(MyData.DeviceData_dir["ADB"]).start_recording()
    print("启动录制")
    # maxtime = maxtime


def stop_record(filename):
    file_path = os.path.join(path_RES_DIR, filename)
    print("file_path", file_path)
    G.DEVICE.stop_recording(output=file_path)
    # G.DEVICE.stop_recording(output=file_path)


def timethis(func):
    """函数运行计时器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        r = func(*args, **kwargs)
        end = time.time()
        print(end - start)
        return r
    return wrapper

def time_difference(time_start):
    """计算时间差"""
    time_end = time.time()  # 结束计时
    time_c = time_end - time_start  # 运行所花时间
    return time_c

def nude_test(fname,scale):
    """裸体检测 False没有 True有裸体"""
    # fname='D:/testimage/1.png'
    # fname = '5.png'
    if os.path.isfile(fname):
        n = Nude(fname,scale)
        n.parse()
        print(n.result)
        print(n.inspect())
        print("hsv_classifier_sum",n.hsv_classifier_sum)
        print("ycbcr_classifier_sum",n.ycbcr_classifier_sum)
        print("rgb_classifier_sum",n.rgb_classifier_sum)
        n.showSkinRegions()
    else:
        print(fname, "is not a file")
    return n.result
def testnude_test():
    """裸体检测测试"""
    CommonDevices1=CommonDevices()
    CommonDevices1=CommonDevices()

    width = G.DEVICE.display_info['width']
    height = G.DEVICE.display_info['height']
    print("width", width)
    print("height", height)
    # #右边
    # starh=int(height * 0.4)
    # starw=int(width * 0.47)
    # endh=int(height * 0.55)
    # endw=int(width*0.7)
    # #左边
    # starh=int(height * 0.46)
    # starw=int(width * 0.25)
    # endh=int(height * 0.55)
    # endw=int(width*0.512)
    #角色
    starh=int(height * 0.1)
    starw=int(width * 0.3)
    endh=int(height * 0.7)
    endw=int(width*0.75)
    IMG_parameter=(starw,starh,endw,endh)
    mysnapshot("lipe",IMG_parameter)
    # myscreenshot("role")
    filename = "lipe" + ".png"
    # filename = "4" + ".png"
    fname=os.path.join(path_RESOURCE_IMAGE,filename)
    # print(filename)
    sleep(3)
    nude_test(fname,60)
# snapshot(filename=filename, msg=filename)
