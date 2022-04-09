#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/18 12:01
# @Author  : v_bkaiwang
# @File    : gui_install_tool_V13.1.py
# @Software: win10 Tensorflow1.13.1 python3.6.3

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import mysql.connector

from mysql.connector import errorcode
import json
import os
import time
import datetime
import logging
from logging.handlers import RotatingFileHandler
import chardet
import shutil
import re
import pymysql
import socket
from tkinter import *
from tkinter import messagebox
import tkinter.font as tkFont
from tkinter.filedialog import askdirectory
import zipfile
import subprocess

if not os.path.exists('./logs'):
    os.mkdir('./logs')
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
# 定义一个RotatingFileHandler，最多备份3个日志文件，每个日志文件最大1K
rHandler = RotatingFileHandler("./logs/deploy.log", maxBytes=4 * 1024 * 1024, backupCount=3)
rHandler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
rHandler.setFormatter(formatter)
logger.addHandler(rHandler)
BASE_SERVE_LIST = ["registercenter", "gateway", "idgenerator", "commonservice", "oss", "facedect"]
_SERVE_LIST = ["device", "tools", "iot", "mj", "xf", "kq", "fk", "qy", "mobile", "lk"]
NACOS_PROT = 8848


# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# console.setFormatter(formatter)
# logger.addHandler(console)


def get_host_ip():
    ip = ''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def deal_file_code(file_path):
    # 处理文件编码转换成utf-8
    with open(file_path, 'rb') as file:
        data = file.read()
        dicts = chardet.detect(data)
    encoding = dicts["encoding"]
    with open(file_path, "r", encoding="{0}".format(encoding)) as f:
        lines = f.readlines()
    with open(file_path, "w", encoding='utf-8') as f:
        for line in lines:
            b_line = line.encode("utf-8")  # 将文件内容转化为utf-8格式
            c_line = b_line.decode("utf-8")
            d_line = re.sub(r'((?<!:)//.*)', '', c_line)
            f.write(d_line)


def read_json(file_path):
    # 读取json配置文件
    # deal_file_code(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def get_service_para(service_name):
    # 获取服务名称，程序路径，解压路径
    # if service_name == 'registercenter':
    #     service_dir_name = r'%s\%s' % (C3iot_path, service_name)
    #     serve_path = r'%s%s' % (service_dir_name, registercenter_path)
    #     serve_file = r'%s%s' % (service_dir_name, registercenter_file)
    #     service_dir_names = [service_dir_name]
    #     serve_paths = [serve_path]
    #     service_files = [serve_file]
    if service_name == 'id-generator':
        service_dir_name = r'%s\c3\basicservice\%s' % (C3iot_path, service_name)
        print(service_dir_name)
        serve_path = r'%s%s' % (service_dir_name, snowflake_path)
        serve_file = r'%s%s' % (service_dir_name, snowflake_file)
        service_dir_names = [service_dir_name]
        serve_paths = [serve_path]
        service_files = [serve_file]
    elif service_name == 'common-service':
        service_dir_name = r'%s\c3\basicservice\%s' % (C3iot_path, service_name)
        print(service_dir_name)
        serve_path = r'%s%s' % (service_dir_name, mqttacl_path)
        serve_file = r'%s%s' % (service_dir_name, mqttacl_file)
        service_dir_names = [service_dir_name]
        serve_paths = [serve_path]
        service_files = [serve_file]
    elif service_name == 'oss':
        service_dir_name = r'%s\c3\basicservice\%s' % (C3iot_path, service_name)
        print(service_dir_name)
        serve_path = r'%s%s' % (service_dir_name, oss_path)
        serve_file = r'%s%s' % (service_dir_name, oss_file)
        service_dir_names = [service_dir_name]
        serve_paths = [serve_path]
        service_files = [serve_file]

    elif service_name == 'face':
        service_dir_name = r'%s\c3\basicservice\%s' % (C3iot_path, service_name)
        print(service_dir_name)
        serve_path = r'%s%s' % (service_dir_name, facdect_path)
        serve_file = r'%s%s' % (service_dir_name, facdect_file)
        service_dir_names = [service_dir_name]
        serve_paths = [serve_path]
        service_files = [serve_file]

    elif service_name == 'iot-login':
        service_dir_name = r'%s\c3\iot\%s' % (C3iot_path, service_name)
        print(service_dir_name)
        serve_path1 = r'%s%s' % (service_dir_name, iotlogin_path)
        serve_file1 = r'%s%s' % (service_dir_name, iotlogin_file)
        service_dir_names = [service_dir_name]
        serve_paths = [serve_path1]
        service_files = [serve_file1]

    elif service_name == 'mobile-api':
        service_dir_name = r'%s\c3\%s' % (C3iot_path, service_name)
        print(service_dir_name)
        serve_path = r'%s%s' % (service_dir_name, mobile_path)
        serve_file = r'%s%s' % (service_dir_name, mobile_file)
        service_dir_names = [service_dir_name]
        serve_paths = [serve_path]
        service_files = [serve_file]

    elif service_name == 'dev-service':
        service_dir_name = r'%s\c3\device\%s' % (C3iot_path, service_name)
        print(service_dir_name)
        serve_path1 = r'%s%s' % (service_dir_name, devservice_path)
        serve_file1 = r'%s%s' % (service_dir_name, devservice_file)
        service_dir_names = [service_dir_name]
        serve_paths = [serve_path1]
        service_files = [serve_file1]

    elif service_name == 'gateway':
        service_dir_name = r'%s\c3\basicservice\%s' % (C3iot_path, service_name)
        print(service_dir_name)
        serve_path = r'%s%s' % (service_dir_name, gateway_path)
        serve_file = r'%s%s' % (service_dir_name, gateway_file)
        service_dir_names = [service_dir_name]
        serve_paths = [serve_path]
        service_files = [serve_file]
        # a = ""
        # with open(lam, "r", encoding="utf-8") as e:
        #     for line in e.read().split('\n'):
        #         if '.jar</arguments>' not in line:
        #             a += line
        #         else:
        #             index = line.find("\\")
        #             i = line[:index] + l + line[index:]
        #             a += i
        #         a += "\n"
        #
        # with open(lam, "w", encoding="utf-8") as w:
        #     for i in a.split("\n"):
        #         w.write(i)
        #         w.write("\n")
        #     w.close()

    elif service_name == 'mj':
        service_dir_name = r'%s\c3\%s' % (C3iot_path, service_name)
        print(service_dir_name)
        serve_path1 = r'%s%s' % (service_dir_name, mj_bgservice_path)
        serve_path2 = r'%s%s' % (service_dir_name, mj_webapi_path)
        serve_file1 = r'%s%s' % (service_dir_name, mj_bgservice_file)
        serve_file2 = r'%s%s' % (service_dir_name, mj_webapi_file)
        service_dir_names = [service_dir_name, service_dir_name]
        serve_paths = [serve_path1, serve_path2]
        service_files = [serve_file1, serve_file2]
    elif service_name == 'xf':
        service_dir_name = r'%s\c3\%s' % (C3iot_path, service_name)
        print(service_dir_name)
        serve_path1 = r'%s%s' % (service_dir_name, xf_bgservice_path)
        serve_path2 = r'%s%s' % (service_dir_name, xf_datamaintain_path)
        serve_file1 = r'%s%s' % (service_dir_name, xf_bgservice_file)
        serve_file2 = r'%s%s' % (service_dir_name, xf_datamaintain_file)
        service_dir_names = [service_dir_name, service_dir_name]
        serve_paths = [serve_path1, serve_path2]
        service_files = [serve_file1, serve_file2]
    elif service_name == 'kq':
        service_dir_name = r'%s\c3\%s' % (C3iot_path, service_name)
        print(service_dir_name)
        serve_path1 = r'%s%s' % (service_dir_name, kq_bgservice_path)
        serve_path2 = r'%s%s' % (service_dir_name, kq_datamaintain_path)
        serve_file1 = r'%s%s' % (service_dir_name, kq_bgservice_file)
        serve_file2 = r'%s%s' % (service_dir_name, kq_datamaintain_file)
        service_dir_names = [service_dir_name, service_dir_name]
        serve_paths = [serve_path1, serve_path2]
        service_files = [serve_file1, serve_file2]
    elif service_name == 'fk':
        service_dir_name = r'%s\c3\%s' % (C3iot_path, service_name)
        print(service_dir_name)
        serve_path1 = r'%s%s' % (service_dir_name, fk_bgservice_path)
        serve_path2 = r'%s%s' % (service_dir_name, fk_datamaintain_path)
        serve_file1 = r'%s%s' % (service_dir_name, fk_bgservice_file)
        serve_file2 = r'%s%s' % (service_dir_name, fk_datamaintain_file)
        service_dir_names = [service_dir_name, service_dir_name]
        serve_paths = [serve_path1, serve_path2]
        service_files = [serve_file1, serve_file2]
    elif service_name == 'qy':
        service_dir_name = r'%s\c3\%s' % (C3iot_path, service_name)
        print(service_dir_name)
        serve_path1 = r'%s%s' % (service_dir_name, qy_bgservice_path)
        serve_path2 = r'%s%s' % (service_dir_name, qy_datamaintain_path)
        serve_file1 = r'%s%s' % (service_dir_name, qy_bgservice_file)
        serve_file2 = r'%s%s' % (service_dir_name, qy_datamaintain_file)
        service_dir_names = [service_dir_name, service_dir_name]
        serve_paths = [serve_path1, serve_path2]
        service_files = [serve_file1, serve_file2]

    else:
        return
    return service_dir_names, serve_paths, service_files


def edit_config_file(file, service, tenant_code, environment, register_center, es_uri, local_address,
                     db_options, db_name, systems):
    print(11075, file, service, tenant_code, environment, register_center, 111111, es_uri, local_address,
          db_options, db_name, systems)
    # 修改配置文件
    if not os.path.exists(file):
        print("配置文件:%s 不存在!请确认文件路径" % file)
        return
    # 同一文件编码为utf-8 xml 报错
    # deal_file_code(file)
    # with open(file, 'r', encoding='utf-8') as f:
    #     con = f.read()
    # con_dict = json.loads(con)

    try:
        db_type = db_options['type']
        ip = db_options["db_ip"]
        user = db_options["user"]
        pwd = db_options["pwd"]
        port = db_options["port"]
        service_port = service['port']

        # if registercenter_file in file:
        #     print("配置注册中心服务Registercenter配置文件")
        #     logger.info("配置注册中心服务Registercenter配置文件")
        #     con_dict['App']['Environment'] = environment
        #     con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
        #     con_dict['DefaultTenantCode'] = tenant_code
        #     con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
        if snowflake_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置雪花算法服务Snowflake配置文件")
            logger.info("配置雪花算法服务Snowflake配置文件")
            # con_dict['App']['Environment'] = environment
            # con_dict['RegisterCenter']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port

            con_dict['SnowFlake']['WorkerID'] = service['work_id']
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)

        elif mqttacl_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置鉴权服务MQTTCal配置文件")
            logger.info("配置鉴权服务MQTTCal配置文件")
            # con_dict['App']['Environment'] = environment
            # con_dict['RegisterCenter']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port
            redis_pass_port = "6379"
            redis_pass_wd = "admin123"
            redis_setting_ = f'{local_address}:{redis_pass_port},password={redis_pass_wd},defaultDatabase=0'
            con_dict['Redis'] = redis_setting_
            con_dict['Mqtt']['Server'] = service['Server']
            con_dict['Global']['DeviceConnect'] = {"Auth": 'false'}
            con_dict['Global']['Login'] = {"OpenImageVerifyCode": False, "IsPrivateDeployment": False}
            # if con_dict['Mqtt']['Server']['Type'] == 'Aliyun':
            #     con_dict['Mqtt']['Aliyun'] = service['mqtt']['Aliyun']
            con_dict['SecretKeyOptions'] = [{"SecretKey": {"id": "361001", "expire": 4782422181, "algorithm": "3DES",
                                                           "Properties": {"key": "1234567887654321",
                                                                          "fillShortKey": "repeat"}}, "Usage": "",
                                             "Remark": ""}]
            con_dict['Rabbitmq']['MqBroker'] = {"Host": local_address, "Port": 5672, "UserName": "admin",
                                                "Password": "das123456"}
            con_dict['Rabbitmq']['DeadExchangeName'] = "dead_exchange"
            con_dict['Rabbitmq']['DeadQueue'] = {"Name": "dead_queue", "MsgExpiration": 259200000}
            con_dict['Rabbitmq']['Queue'] = {"MsgExpiration": 86400000, "Durable": 'true', "MaxPriority": 255,
                                             "ConsumerPerConnect": 3}
            connect_str = con_dict['Dboptions']['connectionstring']
            connect_str = "Server=172.**;Persist Security Info=True;Uid=root;Pwd=***;Database=c3**;port=3306;SslMode=none;Charset=utf8mb4;"
            connect_str = re.sub("Server=(.*?);", "Server=%s;" % ip, connect_str)
            connect_str = re.sub("Uid=(.*?);", "Uid=%s;" % user, connect_str)
            connect_str = re.sub("Pwd=(.*?);", "Pwd=%s;" % pwd, connect_str)
            connect_str = re.sub("Database=(.*?);", "Database=%s;" % db_name, connect_str)
            connect_str = re.sub("port=(\d+)", "port=%s" % port, connect_str)
            con_dict['Dboptions']['connectionstring'] = connect_str
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            print(99017,con_str)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)

        elif oss_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置文件服务OssServer配置文件")
            logger.info("配置文件服务OssServer配置文件")
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port
            # con_dict['App']['Environment'] = environment
            # con_dict['RegisterCenter']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)

        elif facdect_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置人脸检测服务FaceDet配置文件")
            logger.info("配置人脸检测服务FaceDet配置文件")
            # con_dict['App']['Environment'] = environment
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            # con_dict['RegisterCenter']['Address'] = register_center
            con_dict['ArcSDK']['AppKey'] = "GuRA46fYJFu2pNPE6dbiGvSHqrTncJimyhvS2HHsmzaZ"
            con_dict['ArcSDK']['SdkKey'] = "Ecru1yNHuSV4fsSUNRJVG2j7AvpF9B8tpTJrFhZLNyA6"
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port
            # con_dict['MqttServer']['IP'] = mqtt["Server"]["IP"]
            # con_dict['MqttServer']['Port'] = mqtt["Server"]["Port"]
            # con_dict['Server']['FilerServerUrl'] = 'http://%s:6003' % local_address
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)

        elif devservice_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置设备服务DevService配置文件")
            logger.info("配置设备服务DevService配置文件")
            # con_dict['App']['Environment'] = environment
            # con_dict['RegisterCenter']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port
            con_dict['DeviceParser']['Register']['NugetSource'] = 'http://nuget.csdas.cn'
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)

        elif gateway_file in file:
            print("配置网关服务gateway配置文件")
            logger.info("配置网关服务gateway配置文件")
            file_base_ph = os.path.dirname(file)
            a = ""
            with open(file, "r", encoding="utf-8") as e:
                for line in e.read().split('\n'):
                    if '.jar</arguments>' not in line:
                        a += line
                    else:
                        index = line.find("das-gateway")
                        i = line[:index] + file_base_ph + "\\" + line[index:]
                        a += i
                    a += "\n"
                lines = ""
                for i in a.split("\n"):
                    line = f"{local_address}:{NACOS_PROT}"
                    if "172.168.91.234:8848" not in i:
                        lines += i
                    else:
                        c = i.replace("172.168.91.234:8848", line)
                        lines += c
                    lines += "\n"
                print(lines)
            with open(file, "w", encoding="utf-8") as w:
                for i in lines.split("\n"):
                    # print(i)
                    w.write(i)
                    w.write("\n")
                w.close()

            # con_dict['App']['Environment'] = environment
            # con_dict['Register']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            # con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
        elif mj_bgservice_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置门禁bgService服务配置文件")
            logger.info("配置门禁bgService服务配置文件")
            # con_dict['App']['Environment'] = environment
            # con_dict['RegisterCenter']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port

            con_dict['Tenants'][0]['Code'] = tenant_code
            con_dict['Tenants'][0]['DbOptions']['Type'] = db_type
            connect_str = con_dict['Tenants'][0]['DbOptions']['ConnectionString']
            connect_str = "Server=172.**;Persist Security Info=True;Uid=root;Pwd=***;Database=c3**;port=3306;SslMode=none;Charset=utf8mb4;"
            connect_str = re.sub("Server=(.*?);", "Server=%s;" % ip, connect_str)
            connect_str = re.sub("Uid=(.*?);", "Uid=%s;" % user, connect_str)
            connect_str = re.sub("Pwd=(.*?);", "Pwd=%s;" % pwd, connect_str)
            connect_str = re.sub("Database=(.*?);", "Database=%s;" % db_name, connect_str)
            connect_str = re.sub("port=(\d+)", "port=%s" % port, connect_str)
            con_dict['Tenants'][0]['DbOptions']['ConnectionString'] = connect_str
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)

        elif mj_webapi_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置门禁WebAPI服务配置文件")
            logger.info("配置门禁WebAPI服务配置文件")
            # con_dict['App']['Environment'] = environment
            # con_dict['RegisterCenter']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port

            con_dict['Tenants'][0]['Code'] = tenant_code
            con_dict['Tenants'][0]['DbOptions']['Type'] = db_type
            connect_str = con_dict['Tenants'][0]['DbOptions']['ConnectionString']
            connect_str = "Server=172.**;Persist Security Info=True;Uid=root;Pwd=***;Database=c3**;port=3306;SslMode=none;Charset=utf8mb4;"
            connect_str = re.sub("Server=(.*?);", "Server=%s;" % ip, connect_str)
            connect_str = re.sub("Uid=(.*?);", "Uid=%s;" % user, connect_str)
            connect_str = re.sub("Pwd=(.*?);", "Pwd=%s;" % pwd, connect_str)
            connect_str = re.sub("Database=(.*?);", "Database=%s;" % db_name, connect_str)
            connect_str = re.sub("port=(\d+)", "port=%s" % port, connect_str)
            con_dict['Tenants'][0]['DbOptions']['ConnectionString'] = connect_str
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)

        elif xf_bgservice_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置消费服务bgService配置文件")
            logger.info("配置消费服务bgService配置文件")
            # con_dict['App']['Environment'] = environment
            # con_dict['RegisterCenter']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port

            con_dict['Tenants'][0]['Code'] = tenant_code
            con_dict['Tenants'][0]['DbOptions']['Type'] = db_type
            connect_str = con_dict['Tenants'][0]['DbOptions']['ConnectionString']
            connect_str = "Server=172.**;Persist Security Info=True;Uid=root;Pwd=***;Database=c3**;port=3306;SslMode=none;Charset=utf8mb4;"
            connect_str = re.sub("Server=(.*?);", "Server=%s;" % ip, connect_str)
            connect_str = re.sub("Uid=(.*?);", "Uid=%s;" % user, connect_str)
            connect_str = re.sub("Pwd=(.*?);", "Pwd=%s;" % pwd, connect_str)
            connect_str = re.sub("Database=(.*?);", "Database=%s;" % db_name, connect_str)
            connect_str = re.sub("port=(\d+)", "port=%s" % port, connect_str)
            con_dict['Tenants'][0]['DbOptions']['ConnectionString'] = connect_str
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)

        elif xf_datamaintain_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置消费服务datamaintain配置文件")
            logger.info("配置消费datamaintain服务配置文件")
            # con_dict['App']['Environment'] = environment
            # con_dict['RegisterCenter']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            print(9967832, con_dict)
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port

            con_dict['Tenants'][0]['Code'] = tenant_code
            con_dict['Tenants'][0]['DbOptions']['Type'] = db_type
            connect_str = con_dict['Tenants'][0]['DbOptions']['ConnectionString']
            connect_str = "Server=172.**;Persist Security Info=True;Uid=root;Pwd=***;Database=c3**;port=3306;SslMode=none;Charset=utf8mb4;"
            connect_str = re.sub("Server=(.*?);", "Server=%s;" % ip, connect_str)
            connect_str = re.sub("Uid=(.*?);", "Uid=%s;" % user, connect_str)
            connect_str = re.sub("Pwd=(.*?);", "Pwd=%s;" % pwd, connect_str)
            connect_str = re.sub("Database=(.*?);", "Database=%s;" % db_name, connect_str)
            connect_str = re.sub("port=(\d+)", "port=%s" % port, connect_str)
            con_dict['Tenants'][0]['DbOptions']['ConnectionString'] = connect_str
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)

        elif kq_bgservice_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置考勤服务bgService配置文件")
            logger.info("配置考勤服务bgService配置文件")
            # con_dict['App']['Environment'] = environment
            # con_dict['RegisterCenter']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port

            con_dict['Tenants'][0]['Code'] = tenant_code
            con_dict['Tenants'][0]['DbOptions']['Type'] = db_type
            connect_str = con_dict['Tenants'][0]['DbOptions']['ConnectionString']
            connect_str = "Server=172.**;Persist Security Info=True;Uid=root;Pwd=***;Database=c3**;port=3306;SslMode=none;Charset=utf8mb4;"
            connect_str = re.sub("Server=(.*?);", "Server=%s;" % ip, connect_str)
            connect_str = re.sub("Uid=(.*?);", "Uid=%s;" % user, connect_str)
            connect_str = re.sub("Pwd=(.*?);", "Pwd=%s;" % pwd, connect_str)
            connect_str = re.sub("Database=(.*?);", "Database=%s;" % db_name, connect_str)
            connect_str = re.sub("port=(\d+)", "port=%s" % port, connect_str)
            con_dict['Tenants'][0]['DbOptions']['ConnectionString'] = connect_str
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)

        elif kq_datamaintain_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置考勤datamaintain服务配置文件")
            logger.info("配置考勤datamaintain服务配置文件")
            # con_dict['App']['Environment'] = environment
            # con_dict['RegisterCenter']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port

            con_dict['Tenants'][0]['Code'] = tenant_code
            con_dict['Tenants'][0]['DbOptions']['Type'] = db_type
            connect_str = con_dict['Tenants'][0]['DbOptions']['ConnectionString']
            connect_str = "Server=172.**;Persist Security Info=True;Uid=root;Pwd=***;Database=c3**;port=3306;SslMode=none;Charset=utf8mb4;"
            connect_str = re.sub("Server=(.*?);", "Server=%s;" % ip, connect_str)
            connect_str = re.sub("Uid=(.*?);", "Uid=%s;" % user, connect_str)
            connect_str = re.sub("Pwd=(.*?);", "Pwd=%s;" % pwd, connect_str)
            connect_str = re.sub("Database=(.*?);", "Database=%s;" % db_name, connect_str)
            connect_str = re.sub("port=(\d+)", "port=%s" % port, connect_str)
            con_dict['Tenants'][0]['DbOptions']['ConnectionString'] = connect_str
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)

        elif fk_bgservice_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置访客bgService服务配置文件")
            logger.info("配置访客bgService服务配置文件")
            # con_dict['App']['Environment'] = environment
            # con_dict['RegisterCenter']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port

            con_dict['Tenants'][0]['Code'] = tenant_code
            con_dict['Tenants'][0]['DbOptions']['Type'] = db_type
            connect_str = con_dict['Tenants'][0]['DbOptions']['ConnectionString']
            connect_str = "Server=172.**;Persist Security Info=True;Uid=root;Pwd=***;Database=c3**;port=3306;SslMode=none;Charset=utf8mb4;"
            connect_str = re.sub("Server=(.*?);", "Server=%s;" % ip, connect_str)
            connect_str = re.sub("Uid=(.*?);", "Uid=%s;" % user, connect_str)
            connect_str = re.sub("Pwd=(.*?);", "Pwd=%s;" % pwd, connect_str)
            connect_str = re.sub("Database=(.*?);", "Database=%s;" % db_name, connect_str)
            connect_str = re.sub("port=(\d+)", "port=%s" % port, connect_str)
            con_dict['Tenants'][0]['DbOptions']['ConnectionString'] = connect_str
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)

        elif fk_datamaintain_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置访客datamaintain服务配置文件")
            logger.info("配置访客datamaintain服务配置文件")
            # con_dict['App']['Environment'] = environment
            # con_dict['RegisterCenter']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port

            con_dict['Tenants'][0]['Code'] = tenant_code
            con_dict['Tenants'][0]['DbOptions']['Type'] = db_type
            connect_str = con_dict['Tenants'][0]['DbOptions']['ConnectionString']
            connect_str = "Server=172.**;Persist Security Info=True;Uid=root;Pwd=***;Database=c3**;port=3306;SslMode=none;Charset=utf8mb4;"
            connect_str = re.sub("Server=(.*?);", "Server=%s;" % ip, connect_str)
            connect_str = re.sub("Uid=(.*?);", "Uid=%s;" % user, connect_str)
            connect_str = re.sub("Pwd=(.*?);", "Pwd=%s;" % pwd, connect_str)
            connect_str = re.sub("Database=(.*?);", "Database=%s;" % db_name, connect_str)
            connect_str = re.sub("port=(\d+)", "port=%s" % port, connect_str)
            con_dict['Tenants'][0]['DbOptions']['ConnectionString'] = connect_str
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)

        elif qy_bgservice_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置企业bgService服务配置文件")
            logger.info("配置企业bgService服务配置文件")
            # con_dict['App']['Environment'] = environment
            # con_dict['RegisterCenter']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port

            con_dict['Tenants'][0]['Code'] = tenant_code
            con_dict['Tenants'][0]['DbOptions']['Type'] = db_type
            connect_str = con_dict['Tenants'][0]['DbOptions']['ConnectionString']
            connect_str = "Server=172.**;Persist Security Info=True;Uid=root;Pwd=***;Database=c3**;port=3306;SslMode=none;Charset=utf8mb4;"
            connect_str = re.sub("Server=(.*?);", "Server=%s;" % ip, connect_str)
            connect_str = re.sub("Uid=(.*?);", "Uid=%s;" % user, connect_str)
            connect_str = re.sub("Pwd=(.*?);", "Pwd=%s;" % pwd, connect_str)
            connect_str = re.sub("Database=(.*?);", "Database=%s;" % db_name, connect_str)
            connect_str = re.sub("port=(\d+)", "port=%s" % port, connect_str)
            con_dict['Tenants'][0]['DbOptions']['ConnectionString'] = connect_str
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)

        elif qy_datamaintain_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置企业datamaintain服务配置文件")
            logger.info("配置企业datamaintain服务配置文件")
            # con_dict['App']['Environment'] = environment
            # con_dict['RegisterCenter']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port

            con_dict['Tenants'][0]['Code'] = tenant_code
            con_dict['Tenants'][0]['DbOptions']['Type'] = db_type
            connect_str = con_dict['Tenants'][0]['DbOptions']['ConnectionString']
            connect_str = "Server=172.**;Persist Security Info=True;Uid=root;Pwd=***;Database=c3**;port=3306;SslMode=none;Charset=utf8mb4;"
            connect_str = re.sub("Server=(.*?);", "Server=%s;" % ip, connect_str)
            connect_str = re.sub("Uid=(.*?);", "Uid=%s;" % user, connect_str)
            connect_str = re.sub("Pwd=(.*?);", "Pwd=%s;" % pwd, connect_str)
            connect_str = re.sub("Database=(.*?);", "Database=%s;" % db_name, connect_str)
            connect_str = re.sub("port=(\d+)", "port=%s" % port, connect_str)
            con_dict['Tenants'][0]['DbOptions']['ConnectionString'] = connect_str
            con_dict['Tenants'][0]['Systems'] = systems
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)

        elif iotlogin_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置Iotlogin服务配置文件")
            logger.info("配置企业Iotlogin服务配置文件")
            # con_dict['App']['Environment'] = environment
            # con_dict['RegisterCenter']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port

            con_dict['DbOptions']['Type'] = db_type
            connect_str = con_dict['DbOptions']['ConnectionString']
            connect_str = "Server=172.**;Persist Security Info=True;Uid=root;Pwd=***;Database=c3**;port=3306;SslMode=none;Charset=utf8mb4;"
            connect_str = re.sub("Server=(.*?);", "Server=%s;" % ip, connect_str)
            connect_str = re.sub("Uid=(.*?);", "Uid=%s;" % user, connect_str)
            connect_str = re.sub("Pwd=(.*?);", "Pwd=%s;" % pwd, connect_str)
            connect_str = re.sub("Database=(.*?);", "Database=%s;" % db_name, connect_str)
            connect_str = re.sub("port=(\d+)", "port=%s" % port, connect_str)
            con_dict['DbOptions']['ConnectionString'] = connect_str
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)

        elif mobile_file in file:
            deal_file_code(file)
            with open(file, 'r', encoding='utf-8') as f:
                con = f.read()
            print(es_uri, con)
            con_dict = json.loads(con)
            if es_uri:
                con_dict['Logging']['NLog']['ES'] = es_uri
            print("配置iotmobile服务配置文件")
            logger.info("配置企业iotmobile服务配置文件")
            # con_dict['App']['Environment'] = environment
            # con_dict['RegisterCenter']['Address'] = register_center
            # con_dict['App']['ID'] = con_dict['App']['Name'] + '_' + tenant_code
            # con_dict['App']['Addresses'] = ['%s:%s' % (local_address, service_port)]
            con_dict['Nacos']['ServerAddresses'] = [f'http://{local_address}:{NACOS_PROT}']
            con_dict['Nacos']['Ip'] = local_address
            con_dict['Nacos']['Port'] = service_port
            con_dict['DbOptions']['Type'] = db_type
            print(66711, db_type)
            # connect_str = con_dict['DbOptions']['ConnectionString']
            # connect_str = "Server=172.**;Persist Security Info=True;Uid=root;Pwd=***;Database=c3**;port=3306;SslMode=none;Charset=utf8mb4;"
            # connect_str = re.sub("Server=(.*?);", "Server=%s;" % ip, connect_str)
            # connect_str = re.sub("Uid=(.*?);", "Uid=%s;" % user, connect_str)
            # connect_str = re.sub("Pwd=(.*?);", "Pwd=%s;" % pwd, connect_str)
            # connect_str = re.sub("Database=(.*?);", "Database=%s;" % db_name, connect_str)
            # connect_str = re.sub("port=(\d+)", "port=%s" % port, connect_str)
            connect_str = f"Server={ip};Persist Security Info=True;Uid={user};Pwd={pwd};Database={db_name};port={port};SslMode=none;Charset=utf8mb4;"
            print(66711, connect_str)
            con_dict['DbOptions']['ConnectionString'] = connect_str
            print(66711, con_dict)
            con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(con_str)
        else:
            return
        # with open(file, 'w', encoding='utf-8') as f:
        #     f.write(con_str)
    except Exception as e:
        print("修改配置文件%s失败:%s" % (file, e))
        logger.error("修改配置文件%s失败:%s" % (file, e))


def get_sql(sql_path, sql_list):
    # 简单获取sql脚本
    file = os.listdir(sql_path)
    for f in file:
        file_path = sql_path + '/' + f
        if ".sql" in f:
            sql_list.append(file_path)
    return sql_list


def get_real_sql(sql_path, db_type, opt_type, sql_old_version, pag_version, rel_update_dirs):
    print("获取数据库脚本,当前程序版本: %s" % pag_version)
    logger.info("获取数据库脚本,当前程序版本: %s" % pag_version)
    sql_path = sql_path.replace('\\', '/')
    base_sql_path = '%s/%s/base' % (sql_path, db_type)
    update_sql_path = '%s/%s/update' % (sql_path, db_type)
    if opt_type == 'create':
        # 处理基础脚本
        try:
            base_dirs = os.listdir(base_sql_path)
        except Exception as e:
            print(e)
            logger.error(e)
            return rel_update_dirs
        for j in range(len(base_dirs) - 1):
            try:
                for i in range(len(base_dirs) - 1 - j):
                    one_dir = base_dirs[i]
                    tow_dir = base_dirs[i + 1]
                    one_nums = one_dir.split('.')
                    two_nums = tow_dir.split('.')
                    if int(one_nums[0][1:]) > int(two_nums[0][1:]):
                        base_dirs[i], base_dirs[i + 1] = base_dirs[i + 1], base_dirs[i]
                    elif int(one_nums[0][1:]) < int(two_nums[0][1:]):
                        continue
                    elif int(one_nums[0][1:]) == int(two_nums[0][1:]):
                        if int(one_nums[1]) > int(two_nums[1]):
                            base_dirs[i], base_dirs[i + 1] = base_dirs[i + 1], base_dirs[i]
                        elif int(one_nums[1]) < int(two_nums[1]):
                            continue
                        elif int(one_nums[1]) == int(two_nums[1]):
                            if int(one_nums[2]) > int(two_nums[2]):
                                base_dirs[i], base_dirs[i + 1] = base_dirs[i + 1], base_dirs[i]
                            elif int(one_nums[2]) < int(two_nums[2]):
                                continue
            except Exception as e:
                continue

        new_base_version = base_dirs[-1]
        old_version_num = new_base_version.split('.')
        print("执行的基础脚本目录: %s" % new_base_version)
        logger.info("执行的基础脚本目录: %s" % new_base_version)
        rel_update_dirs.append(new_base_version)
        return rel_update_dirs
    else:
        old_version_num = sql_old_version.split('.')
    # 处理更新脚本
    try:
        update_dirs = os.listdir(update_sql_path)
    except:
        print("没有更新脚本")
        logger.warning("没有更新脚本")
        return rel_update_dirs
    # 将更新目录按大小排序
    for j in range(len(update_dirs) - 1):
        try:
            for i in range(len(update_dirs) - 1 - j):
                one_dir = update_dirs[i].split('_')[0]
                tow_dir = update_dirs[i + 1].split('_')[0]
                one_nums = one_dir.split('.')
                two_nums = tow_dir.split('.')
                if int(one_nums[0][1:]) > int(two_nums[0][1:]):
                    update_dirs[i], update_dirs[i + 1] = update_dirs[i + 1], update_dirs[i]
                elif int(one_nums[0][1:]) < int(two_nums[0][1:]):
                    continue
                elif int(one_nums[0][1:]) == int(two_nums[0][1:]):
                    if int(one_nums[1]) > int(two_nums[1]):
                        update_dirs[i], update_dirs[i + 1] = update_dirs[i + 1], update_dirs[i]
                    elif int(one_nums[1]) < int(two_nums[1]):
                        continue
                    elif int(one_nums[1]) == int(two_nums[1]):
                        if int(one_nums[2]) > int(two_nums[2]):
                            update_dirs[i], update_dirs[i + 1] = update_dirs[i + 1], update_dirs[i]
                        elif int(one_nums[2]) < int(two_nums[2]):
                            continue
        except Exception as e:
            logger.info(e)
            continue
    # 获取比上一版本高的更新脚本目录
    new_udpate_dirs = []
    for i in range(len(update_dirs)):
        try:
            update_version = update_dirs[i].split('_')[0]
            update_version_num = update_version.split('.')
            update_one_num = update_version_num[0]
            old_one_num = old_version_num[0]
            if update_one_num.lower().startswith('v'):
                update_one_num = update_one_num[1:]
            if old_one_num.lower().startswith('v'):
                old_one_num = old_one_num[1:]
            if int(update_one_num) > int(old_one_num):
                new_udpate_dirs.append(update_dirs[i])
            elif int(update_one_num) == int(old_one_num):
                if int(update_version_num[1]) > int(old_version_num[1]):
                    new_udpate_dirs.append(update_dirs[i])
                elif int(update_version_num[1]) == int(old_version_num[1]):
                    if int(update_version_num[2]) >= int(old_version_num[2]):
                        new_udpate_dirs.append(update_dirs[i])
        except Exception as e:
            continue
    # 获取比当前版本低的更新脚本目录
    now_version = pag_version.split('.')
    rel_update_dirs = []
    for i in range(len(new_udpate_dirs)):
        try:
            update_version = new_udpate_dirs[i].split('_')[-1]
            update_version_num = update_version.split('.')
            update_one_num = update_version_num[0]
            now_one_num = now_version[0]
            if update_one_num.lower().startswith('v'):
                update_one_num = update_one_num[1:]
            if now_one_num.lower().startswith('v'):
                now_one_num = now_one_num[1:]
            if int(update_one_num) < int(now_one_num):
                rel_update_dirs.append(new_udpate_dirs[i])
            elif int(update_one_num) == int(now_one_num):
                if int(update_version_num[1]) < int(now_version[1]):
                    rel_update_dirs.append(new_udpate_dirs[i])
                elif int(update_version_num[1]) == int(now_version[1]):
                    if int(update_version_num[2]) <= int(now_version[2]):
                        rel_update_dirs.append(new_udpate_dirs[i])
        except Exception as e:
            continue
    print(rel_update_dirs)
    print("需执行的更新脚本目录: %s" % rel_update_dirs)
    logger.info("需执行的更新脚本目录: %s" % rel_update_dirs)

    return rel_update_dirs


def create_db(config, db_name):
    try:
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor()
        sql = "CREATE DATABASE  %s DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;" % db_name
        cur.execute(sql)
        cur.close()
        time.sleep(0.3)
    except Exception as e:
        print(e)
        logger.info(e)


def create_tb(config, db_name):
    try:
        config['database'] = db_name
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor()
        sql2 = "CREATE TABLE `sql_record`  (  `id` int NOT NULL AUTO_INCREMENT,  `update_sql_version` char(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,  `create_time` datetime NULL DEFAULT NULL,  PRIMARY KEY (`id`) USING BTREE) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;"
        cur.execute(sql2)
        cur.close()
        cnx.close()
        time.sleep(0.1)
    except Exception as e:
        print(e)
        logger.info(e)


def get_ret(config, db_name):
    res = []
    config['database'] = db_name
    cnx = mysql.connector.connect(**config)
    cur = cnx.cursor()
    sql = 'select *  from sql_record order by 1 desc limit 0,1;'
    cur.execute(sql)
    for (id, update_sql_version, create_time) in cur:
        res.extend([id, update_sql_version, create_time])
    cur.close()
    cnx.close()
    time.sleep(1)
    return res


def prepare_database(db_option, opt_type, db_name, sql_path, pag_version):
    # 准备数据库
    try:
        ret = []
        db_type = db_option["type"].lower()
        ip = db_option["db_ip"]
        user = db_option["user"]
        pwd = db_option["pwd"]
        port = db_option["port"]
        sql_old_version = db_option["db_old_version"]
        config = {'user': user, 'password': pwd, 'host': ip, 'port': port, 'database': '', 'raise_on_warnings': True,
                  'autocommit': True}
        try:
            if opt_type == 'create':
                create_db(config, db_name)
                create_tb(config, db_name)
            ret = get_ret(config, db_name)
            print(ret)
            if len(ret) == 0:
                sql_old_version = db_option["db_old_version"]
            else:
                sql_old_version = ret[1]
        except Exception as e:
            print(e)
            logger.error(e)
        # sql文件
        rel_update_dirs = []
        rel_update_dirs = get_real_sql(sql_path, db_type, opt_type, sql_old_version, pag_version, rel_update_dirs)
        for i in range(len(rel_update_dirs)):
            new_update_path = ""
            if opt_type == "create":
                new_update_path = '%s/%s/base/%s' % (sql_path, db_type, rel_update_dirs[i])
            else:
                new_update_path = '%s/%s/update/%s' % (sql_path, db_type, rel_update_dirs[i])
            nsql_list = []
            try:
                nsql_list = get_sql(new_update_path, nsql_list)
                if len(nsql_list) > 0:
                    faile_list = {}
                    succ_list = {}
                    for file in nsql_list:
                        try:
                            config['database'] = db_name
                            cnx = mysql.connector.connect(**config)
                            cur = cnx.cursor()  # buffered=True,raw=True
                            with open(file, 'r+', encoding='UTF-8') as f:
                                sql_list = f.read().replace('delimiter', '').replace(';;', '')
                            try:
                                cur.execute(sql_list)
                                cur.close()
                                cnx.close()
                                time.sleep(0.5)
                                dict2 = {file: db_name}
                                succ_list.update(dict2)
                                print("数据库：%s  执行：%s 成功 " % (db_name, file))
                                logger.info("数据库：%s  执行：%s 成功 " % (db_name, file))
                            except Exception as e:
                                dict1 = {file: db_name}
                                faile_list.update(dict1)
                                print("数据库：%s  执行：%s 失败：%s" % (db_name, file, e))
                                logger.error("数据库：%s  执行：%s 失败：%s " % (db_name, file, e))

                        except Exception as e:
                            dict1 = {file: db_name}
                            faile_list.update(dict1)
                            print(e)
                            logger.error(e)
                    if len(succ_list) > 0:
                        connect = pymysql.connect(host=ip, user=user, password=pwd, port=int(port), database=db_name,
                                                  charset='utf8', autocommit=True)
                        cursor = connect.cursor()
                        now_version = '%s' % (rel_update_dirs[i].split('_')[-1])
                        now_time = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
                        sql = "INSERT INTO `sql_record` (update_sql_version,create_time) VALUES ('%s', '%s');" % (
                            now_version, now_time)
                        print(sql)
                        logger.info(sql)
                        cursor.execute(sql)
                        connect.commit()
                    if len(faile_list) > 0:
                        print("失败的sql数量：%s" % len(faile_list))
                        logger.info("失败的sql数量：%s" % len(faile_list))
                        print("失败的sql：%s" % faile_list)
                        logger.info("失败的sql：%s" % faile_list)
            except Exception as e:
                print(e)
                logger.error("失败:%s" % e)
    except Exception as e:
        print(e)
        logger.error(e)


def install_service(service, sev_path):
    # 安装服务
    service_name = service["service_name"]
    service_port = service["port"]
    os.popen("sc stop %s" % service_name)
    time.sleep(2)
    os.popen("sc delete %s" % service_name)
    print(f"delete serve {service_name}")
    time.sleep(1)

    comstr = r'tools\nssm\nssm.exe install %s "%s" "--urls=http://0.0.0.0:%s"' \
             % (service_name, sev_path, service_port)
    ping = subprocess.Popen(comstr, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = ping.communicate()
    print(f"安装服务:{out.decode('gbk')}")

    time.sleep(1)
    opt1 = f'sc start {service_name}'
    lam = subprocess.Popen(opt1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = lam.communicate()
    print(f"开始服务:{out.decode('gbk')}")
    time.sleep(1)


def install_gateway(service, sev_path):
    # 安装gateway服务
    print("7108", service, sev_path)
    service_name = service["service_name"]
    service_port = service["port"]
    os.popen("sc stop %s" % service_name)
    time.sleep(2)
    os.popen("sc delete %s" % service_name)
    time.sleep(2)
    # comstr = r'tools\nssm\nssm.exe install %s "%s" "--urls=http://0.0.0.0:%s"' \
    #          % (service_name, sev_path, service_port)
    filepath, tempfilename = os.path.split(sev_path)
    # 查看乱码打印
    os.system('chcp 65001')
    disk = str(filepath[0]).lower()
    filepath = filepath[2:] + "\\"
    f_string_ = f'{disk}: & {filepath + "das-gateway.exe install"}'
    print(1190, f_string_)
    os.popen(f_string_)
    time.sleep(2)
    opt1 = f'sc start {service_name}'
    print(opt1)
    lam = subprocess.Popen(opt1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = lam.communicate()
    print(f"开始服务:{out.decode('gbk')}")
    time.sleep(2)


def windows_deploy(pag_version, pag_path, db_options, tenant_code, environment, register_center, es_uri,
                   local_address, service, systems):
    # windows服务部署
    try:
        db_name = service.get('db_name', None)
        sev_name = service["service"]
        services = service["services"]
        opt_type = db_options["opt_type"]
        for i in range(len(services)):
            service_name = services[i]["service_name"]
            com_str = r'sc stop %s' % service_name
            print("停止服务:%s" % com_str)
            logger.info("停止服务:%s" % com_str)
            os.popen(com_str)
        # 获取服务参数

        service_dir_names, serve_paths, service_files = get_service_para(sev_name)
        time.sleep(1)
        # 解压文件到对应目录
        if zipfile.is_zipfile(pag_path):
            "判断是不是压缩文件"
            with zipfile.ZipFile(pag_path, 'r') as zipf:
                # zipf.extractall(['E:\\111\\device\\gateway'][0])
                zipf.extractall(service_dir_names[0])

        # # 准备数据库
        if opt_type:
            if db_name:
                print("---------- %s 需进行数据库 %s 操作----------" % (sev_name, opt_type))
                logger.info("---------- %s 需进行数据库 %s 操作----------" % (sev_name, opt_type))
                sql_path = '%s/sql' % (service_dir_names[0].replace('\\', '/'))
                prepare_database(db_options, opt_type, db_name, sql_path, pag_version)
                print("---------- %s 数据库操作完成----------" % sev_name)
                logger.info("---------- %s 数据库操作完成----------" % sev_name)
            else:
                print("%s 无需进行数据库操作..." % sev_name)
                logger.info("%s 无需进行数据库操作..." % sev_name)
        else:
            print("%s 无需进行数据库操作..." % sev_name)
            logger.info("%s 无需进行数据库操作..." % sev_name)

        # 修改配置文件，安装服务
        for i in range(len(services)):
            # 修改配置文件
            service = services[i]
            sev_path = serve_paths[i]
            file = service_files[i]
            print(1111666, file, service, tenant_code, environment, register_center, es_uri,
                  local_address, db_options, db_name, systems)
            try:
                shutil.copy('%s.example' % file, file)
                print("复制文件: %s --> %s" % ('%s.example' % file, file))
                logger.info("复制文件: %s --> %s" % ('%s.example' % file, file))
                time.sleep(1)
            except Exception as e:
                print(e)
                logger.info(e)
                continue
            edit_config_file(file, service, tenant_code, environment, register_center, es_uri,
                             local_address, db_options, db_name, systems)
            print("修改完成！")
            logger.info("修改完成！")
            # 安装服务
            print(sev_path)
            if "gateway" not in file:
                install_service(service, sev_path)
            else:
                install_gateway(service, sev_path)
    except Exception as e:
        print(e)
        logger.error(e)


def docker_deploy(pag_path, tenant_code, environment, register_center, es_uri, local_address, service):
    # docker部署
    pass


def deploy_service(service_type, db_options, tenant_code, environment, register_center, es_uri,
                   local_address, service, systems):
    # 部署服务
    # 根据要部署的服务获取压缩包名
    package_list = os.listdir(package_path)
    pag_name = ''
    sev_name = service["service"]
    for pag in package_list:
        if sev_name in pag:
            pag_name = pag
            print("pag_name:%s" % pag_name)
            break
    if not pag_name:
        print("没有找到%s对应的包..." % sev_name)
        logger.info("没有找到%s对应的包..." % sev_name)
        return
    pag_version_list = pag_name.split('_')[1].split('.')
    pag_version = '%s.%s.%s' % (pag_version_list[0], pag_version_list[1], pag_version_list[2])
    pag_path = r'%s\%s' % (package_path, pag_name)
    if service_type == 'service':
        windows_deploy(pag_version, pag_path, db_options, tenant_code, environment, register_center, es_uri,
                       local_address, service, systems)
    else:
        docker_deploy(pag_path, tenant_code, environment, register_center, es_uri, local_address, service)
    print("\n")


def run_deploy():
    # 读取配置文件数据
    start_time = datetime.datetime.now()
    data = read_json(deply_file_path)
    try:
        # 设置全局变量 部署文件的主路径
        global C3iot_path
        C3iot_path = data["pro_path"]
        service_type = data["type"]
        db_options = data["db_options"]
        tenant_code = data["common"]["tenant_code"]
        environment = data["common"]["environment"]
        register_center = data["common"]["register_center"]
        es_uri = data["common"]["es_uri"]
        local_address = data["common"]["local_address"]
        services_list = data["services"]
        systems = data["systems"]
        if service_type == 'service':
            print("部署类型: windows服务")
            logger.info("部署类型: windows服务")
        elif service_type == 'docker':
            print("部署类型: docker")
            logger.info("部署类型: docker")
        else:
            print("部署类型:%s 暂不支持" % service_type)
            logger.info("部署类型:%s 暂不支持" % service_type)
            return
        print(1723, services_list)
        for i in range(len(services_list)):
            service = services_list[i]
            deploy_service(service_type, db_options, tenant_code, environment, register_center, es_uri,
                           local_address, service, systems)
    except Exception as e:
        print(e)
        logger.error(e)
        messagebox.showinfo('提示', '服务部署失败！\n%s' % e)
        return
    end_time = datetime.datetime.now()
    use_time = end_time - start_time

    print("部署总耗时: %s" % use_time)
    logger.info("部署总耗时: %s" % use_time)
    print("----------部署完成...----------\n\n\n")
    logger.info("----------部署完成...----------\n\n\n\n\n\n")


class MY_GUI():
    def __init__(self, init_window_name):
        lab_row = 0
        self.init_window = init_window_name
        self.ft = tkFont.Font(family='System', size=10, weight=tkFont.BOLD)

        self.init_window.title("部署工具 v1.4.0.0215 mq版")  # 窗口名
        # self.init_window_name.geometry('320x140+10+10')       #290 140为窗口大小，+10 +10 定义窗口弹出时的默认展示位置
        self.init_window.geometry('800x800+620+40')
        # 租户号
        self.ten_lable = Label(self.init_window, text="租户Code", font=self.ft, width=14, anchor=NE)
        self.ten_lable.grid(row=lab_row, column=0, sticky=E)
        default_ten = StringVar()
        default_ten.set('admin')
        self.en_tenant = Entry(self.init_window, width=15, textvariable=default_ten)
        self.en_tenant.grid(row=lab_row, column=1, padx=3, pady=9)
        # 环境变量
        self.env_lable = Label(self.init_window, text="环境变量", font=self.ft, width=14, anchor=NE)
        self.env_lable.grid(row=lab_row, column=2, sticky=E)
        default_env = StringVar()
        default_env.set('production')
        self.en_env = Entry(self.init_window, width=15, textvariable=default_env)
        self.en_env.grid(row=lab_row, column=3, padx=3, pady=9)

        # 本机IP
        self.host_lable = Label(self.init_window, text="本机IP", font=self.ft, width=14, anchor=NE)
        lab_row = lab_row + 1
        self.host_lable.grid(row=lab_row, column=0, sticky=E)
        host_ip = get_host_ip()
        # host_ip = "192.168.13.136"
        default_ip = StringVar()
        default_ip.set(host_ip)
        self.en_webhost = Entry(self.init_window, width=15, textvariable=default_ip)
        self.en_webhost.grid(row=lab_row, column=1, padx=3, pady=0)

        # 注册中心地址
        self.rg_lable = Label(self.init_window, text="注册中心端口", font=self.ft, width=14, anchor=NE)
        # self.rg_lable.grid(row=lab_row, column=2, sticky=E)
        default_rg = StringVar()
        default_rg.set('8000')
        self.en_rg = Entry(self.init_window, width=15, textvariable=default_rg)
        # self.en_rg.grid(row=lab_row, column=3, padx=3, pady=0)

        # 雪花算法ID
        self.snow_ID_lable = Label(self.init_window, text="WorkID", font=self.ft)
        # self.snow_ID_lable.grid(row=lab_row, column=3, sticky=E, padx=3)
        self.snow_ID_lable.grid(row=lab_row, column=2, sticky=E)
        default_snow_ID = StringVar()
        default_snow_ID.set('100')
        self.en_snow_ID = Entry(self.init_window, width=15, textvariable=default_snow_ID)
        # self.en_snow_ID.grid(row=lab_row, column=4, padx=0, pady=0)
        self.en_snow_ID.grid(row=lab_row, column=3, padx=3, pady=0)

        # 数据库地址
        self.db_ip_lable = Label(self.init_window, text="数据库IP地址", font=self.ft)
        lab_row = lab_row + 1
        self.db_ip_lable.grid(row=lab_row, column=0, sticky=E)
        default_db_ip = StringVar()
        default_db_ip.set(host_ip)
        # default_db_ip.set("172.168.91.184")
        self.en_db_ip = Entry(self.init_window, width=15, textvariable=default_db_ip)
        self.en_db_ip.grid(row=lab_row, column=1, padx=3, pady=9)
        # 数据库端口
        self.db_port_lable = Label(self.init_window, text="数据库端口", font=self.ft)
        self.db_port_lable.grid(row=lab_row, column=2, sticky=E)
        default_db_port = StringVar()
        default_db_port.set('3306')
        self.en_db_port = Entry(self.init_window, width=15, textvariable=default_db_port)
        self.en_db_port.grid(row=lab_row, column=3, padx=10, pady=9)

        # 数据库账号
        self.db_user_lable = Label(self.init_window, text="数据库账号", font=self.ft)
        lab_row = lab_row + 1
        self.db_user_lable.grid(row=lab_row, column=0, sticky=E)
        default_db_user = StringVar()
        default_db_user.set('')
        # default_db_user.set('root')
        self.en_db_user = Entry(self.init_window, width=15, textvariable=default_db_user)
        self.en_db_user.grid(row=lab_row, column=1, padx=3, pady=0)

        # 数据库密码
        self.db_pwd_lable = Label(self.init_window, text="数据库密码", font=self.ft)
        self.db_pwd_lable.grid(row=lab_row, column=2, sticky=E)
        default_db_pwd = StringVar()
        default_db_pwd.set('')
        # default_db_pwd.set('123456')
        self.en_db_pwd = Entry(self.init_window, width=15, textvariable=default_db_pwd, show='*')
        self.en_db_pwd.grid(row=lab_row, column=3, padx=3, pady=0)
        # 数据库操作类型
        lab_row = lab_row + 1
        self.db_pwd_lable = Label(self.init_window, text="数据库操作类型", font=self.ft)
        self.db_pwd_lable.grid(row=lab_row, column=0, sticky=E, pady=9)
        self.init_var = IntVar()
        dp_bt = Checkbutton(self.init_window, text="新建", font=self.ft, variable=self.init_var, onvalue=1, offvalue=0,
                            height=1)
        dp_bt.grid(row=lab_row, column=1, sticky=W, padx=3, pady=0)
        self.update_var = IntVar()
        dp_bt = Checkbutton(self.init_window, text="升级", font=self.ft, variable=self.update_var, onvalue=1, offvalue=0,
                            height=1)
        dp_bt.grid(row=lab_row, column=1, sticky=E, padx=3, pady=0)

        # 测试连接数据库
        self.run_bt = Button(self.init_window, text="测试连接", width=13, font=self.ft, bg='lightblue',
                             height=1, command=self.test_connect_db)
        self.run_bt.grid(row=lab_row, column=2, sticky=W, padx=10, pady=0)

        # 数据库上个版本号
        lab_row = lab_row + 1
        self.db_ver_lable = Label(self.init_window, text="数据库上个版本", font=self.ft)
        self.db_ver_lable.grid(row=lab_row, column=0, sticky=E)
        default_db_ver = StringVar()
        default_db_ver.set('v0.0.0')
        self.en_db_ver = Entry(self.init_window, width=15, textvariable=default_db_ver)
        self.en_db_ver.grid(row=lab_row, column=1, padx=0, pady=0)
        self.db_dsp_lable = Label(self.init_window, text="当记录表为空时填写", font=self.ft)
        self.db_dsp_lable.grid(row=lab_row, column=2, sticky=W)

        # 部署路径
        self.pro_lable = Label(self.init_window, text="部署路径", font=self.ft)
        lab_row = lab_row + 1
        self.pro_lable.grid(row=lab_row, column=0, sticky=E, pady=9)
        path = StringVar()
        self.path_bt = Button(self.init_window, text="路径选择", width=13, font=self.ft, bg='lightblue',
                              height=1, command=lambda: self.selectPath(path))
        self.path_bt.grid(row=lab_row, column=2)
        self.en_pro = Entry(self.init_window, width=15, textvariable=path)
        self.en_pro.grid(row=lab_row, column=1, padx=3, pady=0)

        # 基础服务部署
        self.sev_lable = Label(self.init_window, text="基础服务部署", font=self.ft)
        lab_row = 8
        self.sev_lable.grid(row=lab_row, column=0, sticky=E, padx=3, pady=0)
        lab_row = 8
        # self.all_click_var2 = IntVar(value=1)
        #
        # Checkbutton(self.init_window, text='全选/反选', font=self.ft, variable=self.all_click_var2, onvalue=1,
        #             offvalue=0, command="").grid(row=lab_row, column=1, sticky=E, padx=3, pady=9)
        # ------------------------------------######################-----------------------------------------
        # 注册中心

        self.rgs_lable = Label(self.init_window, text="注册中心", font=self.ft)
        lab_row = lab_row + 3
        self.rgs_lable.grid(row=lab_row, column=0, sticky=E, padx=2, pady=0)
        self.rg_var = IntVar(value=1)
        dp_bt = Checkbutton(self.init_window, font=self.ft, variable=self.rg_var, onvalue=1, offvalue=0,
                            height=1)
        dp_bt.grid(row=lab_row, column=0, sticky=W, padx=60, pady=0)

        # 端口
        self.rg_port_lable = Label(self.init_window, text="端口", font=self.ft)
        # self.rg_port_lable.grid(row=lab_row, column=1, sticky=E, padx=3)
        default_rg_port = StringVar()
        default_rg_port.set('8000')
        self.en_rg_port = Entry(self.init_window, width=15, textvariable=default_rg_port)
        # self.en_rg_port.grid(row=lab_row, column=2, padx=0, pady=9)

        # MQTT地址
        self.mqtt_ip_lable = Label(self.init_window, text="MQTT地址", font=self.ft)
        # self.mqtt_ip_lable.grid(row=lab_row, column=3, sticky=E, padx=3)
        default_mqtt_ip = StringVar()
        default_mqtt_ip.set('%s:1883' % host_ip)
        self.en_mqtt_ip = Entry(self.init_window, width=20, textvariable=default_mqtt_ip)
        # self.en_mqtt_ip.grid(row=lab_row, column=4, padx=0, pady=9)

        # 雪花算法服务
        self.snow_lable = Label(self.init_window, text="雪花算法", font=self.ft)
        self.snow_lable.grid(row=lab_row, column=0, sticky=E, padx=3, pady=0)
        self.snow_var = IntVar(value=1)
        dp_bt = Checkbutton(self.init_window, font=self.ft, variable=self.snow_var, onvalue=1, offvalue=0,
                            height=1)
        dp_bt.grid(row=lab_row, column=0, sticky=W, padx=58, pady=0)
        # 端口
        self.snow_port_lable = Label(self.init_window, text="端口", font=self.ft)
        # self.snow_port_lable.grid(row=lab_row, column=1, sticky=E, padx=3)
        default_snow_port = StringVar()
        default_snow_port.set('6001')
        self.en_snow_port = Entry(self.init_window, width=15, textvariable=default_snow_port)
        # self.en_snow_port.grid(row=lab_row, column=2, padx=0, pady=0)

        # 文件服务
        self.oss_lable = Label(self.init_window, text="文件服务", font=self.ft)
        self.oss_lable.grid(row=lab_row, column=1, sticky=E, padx=3, pady=0)
        self.oss_var = IntVar(value=1)
        dp_bt = Checkbutton(self.init_window, font=self.ft, variable=self.oss_var, onvalue=1, offvalue=0,
                            height=1)
        dp_bt.grid(row=lab_row, column=1, sticky=W, padx=60, pady=0)
        # 端口
        self.oss_port_lable = Label(self.init_window, text="端口", font=self.ft)
        # self.oss_port_lable.grid(row=lab_row, column=1, sticky=E, padx=3)
        default_oss_port = StringVar()
        default_oss_port.set('6003')
        self.en_oss_port = Entry(self.init_window, width=15, textvariable=default_oss_port)
        # self.en_oss_port.grid(row=lab_row, column=2, padx=0, pady=0)

        # 人脸检测服务
        self.fac_lable = Label(self.init_window, text="人脸检测", font=self.ft)
        self.fac_lable.grid(row=lab_row, column=2, sticky=E, padx=3, pady=0)
        self.fac_var = IntVar(value=1)
        dp_bt = Checkbutton(self.init_window, font=self.ft, variable=self.fac_var, onvalue=1, offvalue=0,
                            height=1)
        dp_bt.grid(row=lab_row, column=2, sticky=W, padx=60, pady=0)
        # 端口
        self.fac_port_lable = Label(self.init_window, text="端口", font=self.ft)
        # self.fac_port_lable.grid(row=lab_row, column=1, sticky=E, padx=3)
        default_fac_port = StringVar()
        default_fac_port.set('6004')
        self.en_fac_port = Entry(self.init_window, width=15, textvariable=default_fac_port)
        # self.en_fac_port.grid(row=lab_row, column=2, padx=0, pady=0)

        # 网关服务
        self.gate_lable = Label(self.init_window, text="网关服务", font=self.ft)
        # self.gate_lable.grid(row=lab_row, column=3, sticky=E, padx=3, pady=0)
        self.gate_var = IntVar(value=1)
        dp_bt = Checkbutton(self.init_window, font=self.ft, variable=self.gate_var, onvalue=1, offvalue=0,
                            height=1)
        # dp_bt.grid(row=lab_row, column=3, sticky=W, padx=60, pady=0)
        # 端口
        self.gate_port_lable = Label(self.init_window, text="端口", font=self.ft)
        # self.gate_port_lable.grid(row=lab_row, column=1, sticky=E, padx=3)
        default_gate_port = StringVar()
        default_gate_port.set('6012')
        self.en_gate_port = Entry(self.init_window, width=15, textvariable=default_gate_port)
        # self.en_gate_port.grid(row=lab_row, column=2, padx=0, pady=0)

        # 设备服务
        self.dev_lable = Label(self.init_window, text="设备服务", font=self.ft)

        self.dev_lable.grid(row=lab_row, column=3, sticky=E, padx=3, pady=9)
        self.dev_var = IntVar(value=1)
        dp_bt = Checkbutton(self.init_window, font=self.ft, variable=self.dev_var, onvalue=1, offvalue=0,
                            height=1)
        dp_bt.grid(row=lab_row, column=3, sticky=W, padx=60, pady=0)
        # 端口
        self.dev_port_lable = Label(self.init_window, text="端口", font=self.ft)
        # self.dev_port_lable.grid(row=lab_row, column=1, sticky=E, padx=3)
        default_dev_port = StringVar()
        default_dev_port.set('6011')
        self.en_dev_port = Entry(self.init_window, width=15, textvariable=default_dev_port)
        # self.en_dev_port.grid(row=lab_row, column=2, padx=0, pady=0)

        # MQTT鉴权服务

        self.mqtt_lable = Label(self.init_window, text="Common-serve", font=self.ft)
        self.mqtt_lable.grid(row=lab_row, column=4, sticky=E, padx=3, pady=9)
        self.common_var = IntVar(value=1)
        dp_bt = Checkbutton(self.init_window, font=self.ft, variable=self.common_var, onvalue=1, offvalue=0,
                            height=1)
        dp_bt.grid(row=lab_row, column=4, sticky=W, padx=15, pady=0)
        # 数据库名
        self.mqtt_db_lable = Label(self.init_window, text="数据库名", font=self.ft)
        # self.mqtt_db_lable.grid(row=lab_row, column=1, sticky=E, padx=3)
        default_db = StringVar()
        default_db.set('Common_serve')
        self.en_mqttacl_db = Entry(self.init_window, width=15, textvariable=default_db)
        # self.en_mqttacl_db.grid(row=lab_row, column=2, padx=0, pady=0)
        # 后台
        self.mqtt_port_lable = Label(self.init_window, text="后台", font=self.ft)
        # self.mqtt_port_lable.grid(row=lab_row, column=3, sticky=W, padx=3)
        default_mqtt_port = StringVar()
        default_mqtt_port.set('6002')
        self.en_mqtt_port = Entry(self.init_window, width=12, textvariable=default_mqtt_port)
        # self.en_mqtt_port.grid(row=lab_row, column=3, padx=0, pady=0, sticky=E)

        # 统一登陆
        lab_row = lab_row + 1
        self.iot_lable = Label(self.init_window, text="统一登陆", font=self.ft)
        self.iot_lable.grid(row=lab_row, column=0, sticky=E, padx=3, pady=0)
        self.iot_var = IntVar(value=1)
        dp_bt = Checkbutton(self.init_window, font=self.ft, variable=self.iot_var, onvalue=1, offvalue=0,
                            height=1)
        dp_bt.grid(row=lab_row, column=0, sticky=W, padx=60, pady=0)
        # 数据库名
        self.iot_db_lable = Label(self.init_window, text="数据库名", font=self.ft)
        # self.iot_db_lable.grid(row=lab_row, column=1, sticky=E, padx=3)
        default_db = StringVar()
        default_db.set('c3_iotlogin')
        self.en_iot_db = Entry(self.init_window, width=15, textvariable=default_db)
        # self.en_iot_db.grid(row=lab_row, column=2, padx=0, pady=0)
        # 端口
        self.iot_bg_port_lable = Label(self.init_window, text="后台", font=self.ft)
        # self.iot_bg_port_lable.grid(row=lab_row, column=3, sticky=W, padx=3)
        default_iot_bg_port = StringVar()
        default_iot_bg_port.set('6110')
        self.en_iot_bg_port = Entry(self.init_window, width=12, textvariable=default_iot_bg_port)
        # self.en_iot_bg_port.grid(row=lab_row, column=3, padx=0, pady=0, sticky=E)

        # 企业服务
        self.qy_lable = Label(self.init_window, text="企业服务", font=self.ft)
        self.qy_lable.grid(row=lab_row, column=1, sticky=E, padx=3, pady=9)
        self.qy_var = IntVar(value=1)
        dp_bt = Checkbutton(self.init_window, font=self.ft, variable=self.qy_var, onvalue=1, offvalue=0,
                            height=1)
        dp_bt.grid(row=lab_row, column=1, sticky=W, padx=60, pady=0)
        # 数据库名
        self.qy_db_lable = Label(self.init_window, text="数据库名", font=self.ft)
        # self.qy_db_lable.grid(row=lab_row, column=1, sticky=E, padx=3)
        default_db = StringVar()
        default_db.set('c3_qy')
        self.en_qy_db = Entry(self.init_window, width=15, textvariable=default_db)
        # self.en_qy_db.grid(row=lab_row, column=2, padx=0, pady=0)
        # 端口
        self.qy_bg_port_lable = Label(self.init_window, text="后台", font=self.ft)
        # self.qy_bg_port_lable.grid(row=lab_row, column=3, sticky=W, padx=3)
        default_qy_bg_port = StringVar()
        default_qy_bg_port.set('6068')
        self.en_qy_bg_port = Entry(self.init_window, width=12, textvariable=default_qy_bg_port)
        # self.en_qy_bg_port.grid(row=lab_row, column=3, padx=0, pady=0, sticky=E)
        self.qy_dm_port_lable = Label(self.init_window, text="网站", font=self.ft)
        # self.qy_dm_port_lable.grid(row=lab_row, column=4, sticky=W, padx=3)
        default_qy_dm_port = StringVar()
        default_qy_dm_port.set('6069')
        self.en_qy_dm_port = Entry(self.init_window, width=12, textvariable=default_qy_dm_port)
        # self.en_qy_dm_port.grid(row=lab_row, column=4, padx=0, pady=0, sticky=E)

        # 业务服务部署
        self.ssev_lable = Label(self.init_window, text="业务服务部署", font=self.ft)
        nb_row = 18
        self.ssev_lable.grid(row=nb_row, column=0, sticky=E, padx=3, pady=0)

        # 业务全选
        nb_row = 18
        # self.all_click_var = IntVar(value=1)
        # all_bot = Checkbutton(self.init_window, text='全选/反选', font=self.ft, variable=self.all_click_var, onvalue=1,
        #                       offvalue=0, command="").grid(row=nb_row, column=1, sticky=E, padx=3, pady=9)
        # 移动服务
        self.mob_lable = Label(self.init_window, text="移动服务", font=self.ft)
        nb_row = nb_row + 1
        self.mob_lable.grid(row=nb_row, column=0, sticky=E, padx=3, pady=9)
        self.mob_var = IntVar()
        dp_bt = Checkbutton(self.init_window, font=self.ft, variable=self.mob_var, onvalue=1,
                            offvalue=0,
                            height=1)

        dp_bt.grid(row=nb_row, column=0, sticky=W, padx=60, pady=0)
        # 数据库名
        self.mob_db_lable = Label(self.init_window, text="数据库名", font=self.ft)
        # self.mob_db_lable.grid(row=nb_row, column=1, sticky=E, padx=3)
        default_db = StringVar()
        default_db.set('c3_mobile')
        self.en_mob_db = Entry(self.init_window, width=15, textvariable=default_db)
        # self.en_mob_db.grid(row=nb_row, column=2, padx=0, pady=0)
        # 端口
        self.mob_port_lable = Label(self.init_window, text="后台", font=self.ft)
        # self.mob_port_lable.grid(row=nb_row, column=3, sticky=W, padx=3)
        default_mob_port = StringVar()
        default_mob_port.set('6210')
        self.en_mob_port = Entry(self.init_window, width=12, textvariable=default_mob_port)
        # self.en_mob_port.grid(row=nb_row, column=3, padx=0, pady=0, sticky=E)

        # 门禁服务
        self.mj_lable = Label(self.init_window, text="门禁服务", font=self.ft)
        self.mj_lable.grid(row=nb_row, column=1, sticky=E, padx=3, pady=0)
        self.mj_var = IntVar()
        dp_bt = Checkbutton(self.init_window, font=self.ft, variable=self.mj_var, onvalue=1, offvalue=0,
                            height=1)

        dp_bt.grid(row=nb_row, column=1, sticky=W, padx=60, pady=0)
        # 数据库名
        self.mj_db_lable = Label(self.init_window, text="数据库名", font=self.ft)
        # self.mj_db_lable.grid(row=lab_row, column=1, sticky=E, padx=3)
        default_db = StringVar()
        default_db.set('c3_qy')
        self.en_mj_db = Entry(self.init_window, width=15, textvariable=default_db)
        # self.en_mj_db.grid(row=nb_row, column=2, padx=0, pady=0)
        # 端口
        self.mj_bg_port_lable = Label(self.init_window, text="后台", font=self.ft)
        # self.mj_bg_port_lable.grid(row=nb_row, column=3, sticky=W, padx=3)
        default_my_bg_port = StringVar()
        default_my_bg_port.set('6060')
        self.en_mj_bg_port = Entry(self.init_window, width=12, textvariable=default_my_bg_port)
        # self.en_mj_bg_port.grid(row=nb_row, column=3, padx=0, pady=0, sticky=E)
        self.mj_dm_port_lable = Label(self.init_window, text="网站", font=self.ft)
        # self.mj_dm_port_lable.grid(row=nb_row, column=4, sticky=W, padx=3)
        default_mj_dm_port = StringVar()
        default_mj_dm_port.set('6061')
        self.en_mj_dm_port = Entry(self.init_window, width=12, textvariable=default_mj_dm_port)
        # self.en_mj_dm_port.grid(row=nb_row, column=4, padx=0, pady=0, sticky=E)

        # 消费服务
        self.xf_lable = Label(self.init_window, text="消费服务", font=self.ft)
        self.xf_lable.grid(row=nb_row, column=2, sticky=E, padx=3, pady=9)

        self.xf_var = IntVar()
        dp_bt = Checkbutton(self.init_window, font=self.ft, variable=self.xf_var, onvalue=1,
                            offvalue=0,
                            height=1)

        dp_bt.grid(row=nb_row, column=2, sticky=W, padx=60, pady=0)
        # 数据库名
        self.xf_db_lable = Label(self.init_window, text="数据库名", font=self.ft)
        # self.xf_db_lable.grid(row=nb_row, column=1, sticky=E, padx=3)
        default_db = StringVar()
        default_db.set('c3_xf')
        self.en_xf_db = Entry(self.init_window, width=15, textvariable=default_db)
        # self.en_xf_db.grid(row=nb_row, column=2, padx=0, pady=0)
        # 端口
        self.xf_bg_port_lable = Label(self.init_window, text="后台", font=self.ft)
        # self.xf_bg_port_lable.grid(row=nb_row, column=3, sticky=W, padx=3)
        default_xf_bg_port = StringVar()
        default_xf_bg_port.set('6062')
        self.en_xf_bg_port = Entry(self.init_window, width=12, textvariable=default_xf_bg_port)
        # self.en_xf_bg_port.grid(row=nb_row, column=3, padx=0, pady=0, sticky=E)
        self.xf_dm_port_lable = Label(self.init_window, text="网站", font=self.ft)
        # self.xf_dm_port_lable.grid(row=nb_row, column=4, sticky=W, padx=3)
        default_xf_dm_port = StringVar()
        default_xf_dm_port.set('6063')
        self.en_xf_dm_port = Entry(self.init_window, width=12, textvariable=default_xf_dm_port)
        # self.en_xf_dm_port.grid(row=nb_row, column=4, padx=0, pady=0, sticky=E)

        # 考勤服务
        self.kq_lable = Label(self.init_window, text="考勤服务", font=self.ft)
        self.kq_lable.grid(row=nb_row, column=3, sticky=E, padx=3, pady=0)
        self.kq_var = IntVar()
        dp_bt = Checkbutton(self.init_window, font=self.ft, variable=self.kq_var, onvalue=1,
                            offvalue=0,
                            height=1)
        dp_bt.grid(row=nb_row, column=3, sticky=W, padx=60, pady=0)
        # 数据库名
        self.kq_db_lable = Label(self.init_window, text="数据库名", font=self.ft)
        # self.kq_db_lable.grid(row=nb_row, column=1, sticky=E, padx=3)
        default_db = StringVar()
        default_db.set('c3_kq')
        self.en_kq_db = Entry(self.init_window, width=15, textvariable=default_db)
        # self.en_kq_db.grid(row=nb_row, column=2, padx=0, pady=0)
        # 端口
        self.kq_bg_port_lable = Label(self.init_window, text="后台", font=self.ft)
        # self.kq_bg_port_lable.grid(row=nb_row, column=3, sticky=W, padx=3)
        default_kq_bg_port = StringVar()
        default_kq_bg_port.set('6064')
        self.en_kq_bg_port = Entry(self.init_window, width=12, textvariable=default_kq_bg_port)
        # self.en_kq_bg_port.grid(row=nb_row, column=3, padx=0, pady=0, sticky=E)
        self.kq_dm_port_lable = Label(self.init_window, text="网站", font=self.ft)
        # self.kq_dm_port_lable.grid(row=nb_row, column=4, sticky=W, padx=3)
        default_kq_dm_port = StringVar()
        default_kq_dm_port.set('6065')
        self.en_kq_dm_port = Entry(self.init_window, width=12, textvariable=default_kq_dm_port)
        # self.en_kq_dm_port.grid(row=nb_row, column=4, padx=0, pady=0, sticky=E)

        # 访客服务
        self.fk_lable = Label(self.init_window, text="访客服务", font=self.ft)
        self.fk_lable.grid(row=nb_row, column=4, sticky=E, padx=3, pady=9)

        self.fk_var = IntVar()
        dp_bt = Checkbutton(self.init_window, font=self.ft, variable=self.fk_var, onvalue=1,
                            offvalue=0,
                            height=1)

        dp_bt.grid(row=nb_row, column=4, sticky=W, padx=60, pady=0)
        # 数据库名
        self.fk_db_lable = Label(self.init_window, text="数据库名", font=self.ft)
        # self.fk_db_lable.grid(row=nb_row, column=1, sticky=E, padx=3)
        default_db = StringVar()
        default_db.set('c3_fk')
        self.en_fk_db = Entry(self.init_window, width=15, textvariable=default_db)
        # self.en_fk_db.grid(row=nb_row, column=2, padx=0, pady=0)
        # 端口
        self.fk_bg_port_lable = Label(self.init_window, text="后台", font=self.ft)
        # self.fk_bg_port_lable.grid(row=nb_row, column=3, sticky=W, padx=3)
        default_fk_bg_port = StringVar()
        default_fk_bg_port.set('6066')
        self.en_fk_bg_port = Entry(self.init_window, width=12, textvariable=default_fk_bg_port)
        # self.en_fk_bg_port.grid(row=nb_row, column=3, padx=0, pady=0, sticky=E)
        self.fk_dm_port_lable = Label(self.init_window, text="网站", font=self.ft)
        # self.fk_dm_port_lable.grid(row=nb_row, column=4, sticky=W, padx=3)
        default_fk_dm_port = StringVar()
        default_fk_dm_port.set('6067')
        self.en_fk_dm_port = Entry(self.init_window, width=12, textvariable=default_fk_dm_port)
        # self.en_fk_dm_port.grid(row=nb_row, column=4, padx=0, pady=0, sticky=E)

        # def button_Click(event=None):
        #     print(fac_var.get())
        #
        # lab_row = lab_row + 1
        # b1 = Button(self.init_window, text='click me', relief='raised', width=8, height=1, command=button_Click)
        # b1.grid(row=lab_row, column=1, sticky=W, padx=60, pady=0)

        # 执行用例
        # lab_row = lab_row + 1
        lab_row += 100
        self.run_bt = Button(self.init_window, text="开始部署", width=15, font=self.ft, bg='lightblue',
                             height=2, command=self.run)
        self.run_bt.grid(row=lab_row, column=1, sticky=W, padx=3, pady=15)

        self.start_bt = Button(self.init_window, text="启动服务", width=15, font=self.ft, bg='lightblue',
                               height=2, command=self.start_service)
        self.start_bt.grid(row=lab_row, column=2, sticky=W, padx=3, pady=15)

        self.stop_bt = Button(self.init_window, text="停止服务", width=15, font=self.ft, bg='lightblue',
                              height=2, command=self.stop_service)
        self.stop_bt.grid(row=lab_row, column=3, sticky=W, padx=3, pady=15)

        self.bak_bt = Button(self.init_window, text="备份数据库", width=15, font=self.ft, bg='lightblue',
                             height=2, command=self.bak_service)
        self.bak_bt.grid(row=lab_row, column=4, sticky=W, padx=3, pady=15)

    def start_service(self):
        # 启动服务
        ret = self.deal_deploy_file()
        if not ret:
            return
        try:
            data = read_json(deply_file_path)
            services_list = data["services"]
            pro_path = data["pro_path"]
            systems = data["systems"]
            for i in range(len(services_list)):
                service = services_list[i]
                service_name = service["service"]
                services = service["services"]
                if service_name == 'qy':
                    try:
                        file = r'%s\qy\%s' % (pro_path, qy_datamaintain_file)
                        with open(file, 'r', encoding='utf-8') as f:
                            con = f.read()
                        con_dict = json.loads(con)
                        con_dict['Tenants'][0]['Systems'] = systems
                        con_str = json.dumps(con_dict, indent=2, ensure_ascii=False)
                        with open(file, 'w', encoding='utf-8') as f:
                            f.write(con_str)
                    except:
                        pass
                for j in range(0, len(services)):
                    ser_name = services[j]["service_name"]
                    com_str = r'sc start %s' % ser_name
                    print("启动服务:%s" % com_str)
                    logger.info("启动服务:%s" % com_str)
                    ret = os.popen(com_str).read()
                    print(ret)
                    logger.info(ret)
                    time.sleep(0.5)
            messagebox.showinfo('提示', '服务启动完成！')
        except Exception as e:
            messagebox.showinfo('提示', '服务启动失败！\n%s' % e)

    def stop_service(self):
        # 停止服务
        ret = self.deal_deploy_file()
        if not ret:
            return
        try:
            data = read_json(deply_file_path)
            services_list = data["services"]
            for i in range(len(services_list)):
                service = services_list[i]
                services = service["services"]
                for j in range(0, len(services)):
                    ser_name = services[j]["service_name"]
                    com_str = r'sc stop %s' % ser_name
                    print("停止服务:%s" % com_str)
                    logger.info("停止服务:%s" % com_str)
                    ret = os.popen(com_str).read()
                    print(ret)
                    logger.info(ret)
                    time.sleep(0.5)
            messagebox.showinfo('提示', '停止服务完成！')
        except Exception as e:
            messagebox.showinfo('提示', '停止服务失败！\n%s' % e)

    def bak_service(self):
        ret = messagebox.askquestion(title='提示', message='数据备份时：\n请注意观察是否有错误\n请注意观察是否有错误\n请注意观察是否有错误')
        if ret != 'yes':
            return
        print("开始备份数据")
        logger.info("开始备份数据")
        now_time1 = datetime.datetime.strftime(datetime.datetime.now(), "%Y_%m_%d_%H%M%S")
        checkdir(now_path + "/database_bak/")
        checkdir(now_path + "/database_bak/" + now_time1)
        deal_file_code(deply_file_path)
        data = read_json(deply_file_path)
        dbip = data['db_options']['db_ip']
        dbport = data['db_options']['port']
        dbusr = data['db_options']['user']
        dbpwd = data['db_options']['pwd']
        dbs = []
        try:
            con = pymysql.connect(host=dbip, user=dbusr, password=dbpwd, port=int(dbport), connect_timeout=10)
            cur = con.cursor()
            if cur:
                print('数据库连接成功')
                sql = "show DATABASES like '%c3_%'"
                cur.execute(sql)
                ret = cur.fetchall()
                dbs = ret
                print(ret)
            cur.close()
        except Exception as e:
            print(e)
            messagebox.showinfo('提示', '连接数据库服务失败！请检查配置文件\n%s' % e)
            return
        for db in dbs:
            bakfile = now_path + "/database_bak/" + now_time1 + '/' + str(db[0]) + ".db"
            bakfile1 = bakfile.replace('/', '\\')
            comstr = r"tools\mysql\bin\mysqldump -h%s -P%s -u%s -p%s %s >%s" % (
                dbip, dbport, dbusr, dbpwd, str(db[0]), bakfile1)
            comstr2 = r"tools\mysql\bin\mysqldump -h%s -P%s -u%s -p%s %s >%s" % (
                dbip, dbport, dbusr, "***", str(db[0]), bakfile1)
            print(comstr2)
            try:
                print(os.popen(comstr).read())
            except Exception as e:
                logger.error(e)
                print(e)
        messagebox.showinfo('提示', '数据备份完成。\n请检查数据是否备份完整。')

    def selectPath(self, path):
        path_ = askdirectory().replace('/', '\\')
        path.set(path_)

    def test_connect_db(self):
        # 测试连接数据库
        db_ip = self.en_db_ip.get()
        db_user = self.en_db_user.get()
        db_pwd = self.en_db_pwd.get()
        db_port = self.en_db_port.get()
        try:
            con = pymysql.connect(host=db_ip, user=db_user, password=db_pwd, port=int(db_port), connect_timeout=10)
            cur = con.cursor()
            if cur:
                messagebox.showinfo('提示', '连接成功')
            cur.close()
        except Exception as e:
            print(e)
            messagebox.showinfo('提示', '连接数据库服务失败！\n%s' % e)

    def deal_deploy_file(self):
        # 读写部署文件
        ten_code = self.en_tenant.get()
        env_value = self.en_env.get()
        webhost = self.en_webhost.get()
        rg_url = webhost + ':' + self.en_rg.get()
        db_ip = self.en_db_ip.get()
        db_port = self.en_db_port.get()
        db_user = self.en_db_user.get()
        db_pwd = self.en_db_pwd.get()
        init_opt = self.init_var.get()
        update_opt = self.update_var.get()
        db_old_ver = self.en_db_ver.get()
        pro_pt = self.en_pro.get()
        rg_var = self.rg_var.get()
        # rg_var = self.all_click_var2.get()
        rg_port = self.en_rg_port.get()
        snow_var = self.snow_var.get()
        # snow_var = self.all_click_var2.get()
        snow_port = self.en_snow_port.get()
        snow_ID = self.en_snow_ID.get()
        common_var = self.common_var.get()
        # common_var = self.all_click_var2.get()
        mqtt_port = self.en_mqtt_port.get()
        mqtt_ip = self.en_mqtt_ip.get()
        mqtt_db = self.en_mqttacl_db.get()
        oss_var = self.oss_var.get()
        # oss_var = self.all_click_var2.get()
        oss_port = self.en_oss_port.get()
        fac_var = self.fac_var.get()
        # fac_var = self.all_click_var2.get()
        fac_port = self.en_fac_port.get()
        gate_var = self.gate_var.get()
        # gate_var = self.all_click_var2.get()
        gate_port = self.en_gate_port.get()
        dev_var = self.dev_var.get()
        # dev_var = self.all_click_var2.get()
        dev_port = self.en_dev_port.get()
        qy_var = self.qy_var.get()
        # qy_var = self.all_click_var2.get()
        qy_db = self.en_qy_db.get()
        qy_bg_port = self.en_qy_bg_port.get()
        qy_dm_port = self.en_qy_dm_port.get()

        mj_var = self.mj_var.get()
        # mj_var = self.all_click_var.get()
        mj_db = self.en_mj_db.get()
        mj_bg_port = self.en_mj_bg_port.get()
        mj_dm_port = self.en_mj_dm_port.get()
        xf_var = self.xf_var.get()
        # xf_var = self.all_click_var.get()
        xf_db = self.en_xf_db.get()
        xf_bg_port = self.en_xf_bg_port.get()
        xf_dm_port = self.en_xf_dm_port.get()
        kq_var = self.kq_var.get()
        # kq_var = self.all_click_var.get()
        kq_db = self.en_kq_db.get()
        kq_bg_port = self.en_kq_bg_port.get()
        kq_dm_port = self.en_kq_dm_port.get()
        fk_var = self.fk_var.get()
        # fk_var = self.all_click_var.get()
        fk_db = self.en_fk_db.get()
        fk_bg_port = self.en_fk_bg_port.get()
        fk_dm_port = self.en_fk_dm_port.get()
        iot_var = self.iot_var.get()
        iot_db = self.en_iot_db.get()
        iot_bg_port = self.en_iot_bg_port.get()
        mob_var = self.mob_var.get()
        # mob_var = self.all_click_var.get()
        mob_db = self.en_mob_db.get()
        mob_bg_port = self.en_mob_port.get()

        if init_opt and update_opt:
            messagebox.showinfo('提示', '数据库操作类型只能选新建或升级或两者都不选(不进行任何操作)')
            return
        # messagebox.showinfo('提示', '部署可能需要几分钟,请耐心等待...\n\n部署过程中请不要频繁点击或关闭部署程序')
        # 将传入的参数写入json文件
        data = read_json(deply_file_path)
        services = []
        systems = data["systems"]
        if rg_var:
            serv_data = {"service": "gateway", "descript": "注册中心服务",
                         "services": [{"service_name": "das-gateway", "port": "%s" % rg_port}]
                         }
            services.append(serv_data)
        if snow_var:
            serv_data = {"service": "id-generator", "descript": "雪花算法服务",
                         # "services": [{"service_name": "das-microservice-snowflake",
                         "services": [{"service_name": "das-id-generator",
                                       "port": "%s" % snow_port, "work_id": int(snow_ID)}]
                         }
            services.append(serv_data)
        if common_var:
            ip = mqtt_ip.split(':')[0]
            port = mqtt_ip.split(':')[-1]
            serv_data = {"service": "common-service", "descript": "commom-serve", "db_name": "%s" % mqtt_db,
                         "services": [{"service_name": "das-common-service", "port": "%s" % mqtt_port,
                                       "Server": {"Type": "Emqx", "IP": "%s" % ip, "Port": int(port)}}]
                         }
            services.append(serv_data)
        if oss_var:
            serv_data = {"service": "oss", "descript": "oss文件服务",
                         "services": [{"service_name": "das-oss", "port": "%s" % oss_port}]
                         }
            services.append(serv_data)
        if fac_var:
            serv_data = {"service": "face", "descript": "人脸检测服务",
                         "services": [{"service_name": "das-face_dect", "port": "%s" % fac_port}]
                         }
            services.append(serv_data)
        # if gate_var:
        #     serv_data = {"service": "", "descript": "网关服务",
        #                  "services": [{"service_name": "das-device-gateway", "port": "%s" % gate_port}]
        #                  }
        #     services.append(serv_data)
        if mj_var:
            serv_data = {"service": "mj", "descript": "门禁服务", "db_name": "%s" % mj_db,
                         "services": [{"service_name": "das-mj-core", "descript": "门禁后台服务",
                                       "port": "%s" % mj_bg_port},
                                      {"service_name": "das-mj-webapi", "descript": "门禁网站服务",
                                       "port": "%s" % mj_dm_port}]
                         }
            system_data = {"Name": "mj", "Apps": {"UI": "mj_webapi"}}
            services.append(serv_data)
            if system_data not in systems:
                systems.append(system_data)
        if xf_var:
            serv_data = {"service": "xf", "descript": "消费服务", "db_name": "%s" % xf_db,
                         "services": [{"service_name": "das-xf-core", "descript": "消费后台服务",
                                       "port": "%s" % xf_bg_port},
                                      {"service_name": "das-xf-webapi", "descript": "消费网站服务",
                                       "port": "%s" % xf_dm_port}]
                         }
            system_data = {"Name": "xf", "Apps": {"UI": "xf_dm"}}
            services.append(serv_data)
            if system_data not in systems:
                systems.append(system_data)
        if kq_var:
            serv_data = {"service": "kq", "descript": "考勤服务", "db_name": "%s" % kq_db,
                         "services": [{"service_name": "das-kq-core", "descript": "考勤后台服务",
                                       "port": "%s" % kq_bg_port},
                                      {"service_name": "das-kq-webapi", "descript": "考勤网站服务",
                                       "port": "%s" % kq_dm_port}]
                         }
            system_data = {"Name": "kq", "Apps": {"UI": "kq_dm"}}
            services.append(serv_data)
            if system_data not in systems:
                systems.append(system_data)
        if fk_var:
            serv_data = {"service": "fk", "descript": "访客服务", "db_name": "%s" % fk_db,
                         "services": [{"service_name": "das-fk-core", "descript": "访客后台服务",
                                       "port": "%s" % fk_bg_port},
                                      {"service_name": "das-fk-webapi", "descript": "访客网站服务",
                                       "port": "%s" % fk_dm_port}]
                         }
            system_data = {"Name": "fk", "Apps": {"UI": "fk_dm"}}
            services.append(serv_data)
            if system_data not in systems:
                systems.append(system_data)
        if qy_var:
            serv_data = {"service": "qy", "descript": "企业服务", "db_name": "%s" % qy_db,
                         "services": [{"service_name": "das-qy-core", "descript": "企业后台服务",
                                       "port": "%s" % qy_bg_port},
                                      {"service_name": "das-qy-webapi", "descript": "企业网站服务",
                                       "port": "%s" % qy_dm_port}],
                         }
            services.append(serv_data)
        if dev_var:
            serv_data = {"service": "dev-service", "descript": "设备服务",
                         "services": [{"service_name": "das-dev-service", "port": "%s" % dev_port}]
                         }
            services.append(serv_data)

        if iot_var:
            serv_data = {"service": "iot-login", "descript": "Iot", "db_name": "%s" % iot_db,
                         "services": [{"service_name": "das-iot-login", "port": "%s" % iot_bg_port}]
                         }
            services.append(serv_data)
        if mob_var:
            serv_data = {"service": "mobile-api", "descript": "Iot", "db_name": "%s" % mob_db,
                         "services": [{"service_name": "das-iot-mobile", "port": "%s" % mob_bg_port}]
                         }
            services.append(serv_data)
        data["systems"] = systems
        data["common"]["tenant_code"] = ten_code
        data["common"]["environment"] = env_value
        if init_opt:
            data["db_options"]["opt_type"] = "create"
            data["db_options"]["db_old_version"] = ""
        if update_opt:
            data["db_options"]["opt_type"] = "update"
            data["db_options"]["db_old_version"] = db_old_ver
        if not init_opt and not update_opt:
            data["db_options"]["opt_type"] = ""
            data["db_options"]["db_old_version"] = ""
        data["pro_path"] = pro_pt
        data["db_options"]["db_ip"] = db_ip
        data["db_options"]["user"] = db_user
        data["db_options"]["pwd"] = db_pwd
        data["db_options"]["port"] = db_port
        data["common"]["local_address"] = webhost
        data["common"]["register_center"] = rg_url
        data["services"] = services

        # self.touch_file(data["pro_path"], )

        data_str = json.dumps(data, ensure_ascii=False, indent=2)
        with open(deply_file_path, 'w', encoding='utf-8') as f:
            f.write(data_str)
        time.sleep(0.5)
        return 1

    def run(self):
        # 获取传入的参数
        ret = messagebox.askquestion(title='提示', message='数据是否已备份？')
        if ret != 'yes':
            return

        ret = self.deal_deploy_file()
        if not ret:
            return
        # # 开始部署
        run_deploy()
        messagebox.showinfo('提示', '部署完成！')


def checkdir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def main():
    print("----------开始部署...----------")
    logger.info("----------开始部署...----------")
    init_window = Tk()  # 实例化出一个父窗口
    gui = MY_GUI(init_window)
    # # 设置根窗口默认属性

    init_window.mainloop()


# 获取当前程序路径

now_path = os.getcwd()
# now_path = os.path.dirname(os.path.realpath(__file__))
logger.info(now_path)

# 解压后的程序路径
deply_file_path = r'%s\c3iot_deploy.json' % now_path
# deply_file_path = r'G:\C3_iot\items\c3iot_deploy.json'
nssm_pt = r'%s\tools\Nssm' % now_path
mysql_pt = r'%s\tools\mysql\bin' % now_path
package_path = r'%s\package' % now_path
dll_140_path = r'%s\vcruntime140.dll' % mysql_pt
dll_msvcp140_path = r'%s\msvcp140.dll' % mysql_pt
# 复制dll文件到system32
try:
    shutil.copy(dll_140_path, r'C:\Windows\System32\vcruntime140.dll')
    shutil.copy(dll_msvcp140_path, r'C:\Windows\System32\msvcp140.dll')
except Exception as e:
    logger.info(e)
# 程序绝对路径
# registercenter_path = r'\bin\das.id-generator.exe'
# registercenter_file = r'\config\registercentr_settings.json'
# 雪花算法
snowflake_path = r'\bin\das.id-generator.exe'
snowflake_file = r'\config\id-generator.json'
# mqtt鉴权
mqttacl_path = r'\bin\das.common-service.exe'
mqttacl_file = r'\config\common-service.json'
# 文件服务
oss_path = r'\bin\das.oss.exe'
oss_file = r'\config\oss_settings.json'
# 人脸检测
facdect_path = r'\bin\das.face-dect.exe'
facdect_file = r'\config\face-dect.json'
# 统一登录
iotlogin_path = r'\bin\das.iot-login.exe'
iotlogin_file = r'\config\iot-login.json'
# 设备服务
devservice_path = r'\bin\das.dev-service.exe'
devservice_file = r'\config\dev-service.json'
# 网关服务&注册中心
gateway_path = r'\gateway\das-gateway.exe'
# gateway_file = r'\gateway\gateway-0.0.1.031402.xml'
gateway_file = r'\gateway\das-gateway.xml'
# 门禁
# bg=core
mj_bgservice_path = r'\mj-core\bin\das.mj-core.exe'
mj_bgservice_file = r'\mj-core\config\mj-core.json'

mj_webapi_path = r'\mj-webapi\bin\das.mj-webapi.exe'
mj_webapi_file = r'\mj-webapi\config\mj-webapi.json'

# 消费
xf_bgservice_path = r'\xf-core\bin\das.xf-core.exe'
xf_bgservice_file = r'\xf-core\config\xf-core.json'
xf_datamaintain_path = r'\xf-webapi\bin\das.xf-webapi.exe'
xf_datamaintain_file = r'\xf-webapi\config\xf-webapi.json'
# 考勤
kq_bgservice_path = r'\kq-core\bin\das.kq-core.exe'
kq_bgservice_file = r'\kq-core\config\kq-core.json'

kq_datamaintain_path = r'\kq-webapi\bin\das.kq-webapi.exe'
kq_datamaintain_file = r'\kq-webapi\config\kq-webapi.json'
# 访客
fk_bgservice_path = r'\fk-core\bin\das.fk-core.exe'
fk_bgservice_file = r'\fk-core\config\fk-core.json'

fk_datamaintain_path = r'\fk-webapi\bin\das.fk-webapi.exe'
fk_datamaintain_file = r'\fk-webapi\config\fk-webapi.json'
# 企业
qy_bgservice_path = r'\qy-core\bin\das.qy-core.exe'
qy_bgservice_file = r'\qy-core\config\qy-core.json'

qy_datamaintain_path = r'\qy-webapi\bin\das.qy-webapi.exe'
qy_datamaintain_file = r'\qy-webapi\config\qy-webapi.json'
# 移动后台
mobile_path = r'\mobile-api\bin\das.mobile-api.exe'
mobile_file = r'\mobile-api\config\mobile-api.json'

# 部署完之后输入
"""
INSERT INTO `tenant_self_cfg`(`id`, `tenant_code`, `cfg_type`, `cfg_sort`, `cfg_code`, `cfg_value`, `remarks`)      VALUES (1, 'admin', 'StringArray', 0, 'PcWebBiz', '[\"xt\",\"qy\",\"mj\",\"xf\",\"kq\",\"fk\"]', '');
"""

if __name__ == '__main__':
    main()

