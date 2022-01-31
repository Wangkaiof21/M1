#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/17 17:44
# @Author  : v_bkaiwang
# @File    : stfp-tool.py
# @Software: win10 Tensorflow1.13.1 python3.6.3

import os
import re
import stat
import argparse
import telnetlib
from functools import partial
import paramiko


def print_log(quiet, content):
    if not quiet:
        print(content)


# TODO:telnet


class Terminal:

    def __init__(self, host_name, user, pwd, port, host_type='ssh', quiet=False, log=print_log):
        self.host_type = host_type
        self.host_name = host_name
        self.user = user
        self.pwd = pwd
        self.port = port

        self.enter_char = '\n'
        self.login_head = ''
        self.pattern = re.compile(r'.*?[@|:].*?[\n]*?[#|$]')
        self.scale_factor = 1

        self.log: log = partial(log, quiet)  # 类func = functools.partial(func, *args, **keywords)

        self.term = None
        self.is_connect = False

        self.connect()

    def _check_first_login(self):
        """
        创建telnet对象后 敲回车 看是否返回'root@wing:~#' 或者[root@j7896907.spa.eu95]
        若返回 则说明连接成功
        :return:
        """
        self.term.write(f'{self.enter_char}'.encode('utf-8'))
        # 临时的超时时间
        tmp_timeout = self.scale_factor * 0.5
        check_res = (self.term.read_until('#'.encode('utf-8'), timeout=tmp_timeout)).decode('utf-8')
        login_head = self.pattern.findall(check_res)
        try:
            login_head = login_head[0]
        except IndexError as e:
            self.log(f'{e}, 有人在操作此机器')
        connect_status = True if login_head else False
        self.login_head = login_head
        return connect_status

    def connect(self):
        try:
            if self.host_type == 'ssh':
                self.term = paramiko.SSHClient()
                # 加载白名单
                self.term.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.term.connect(hostname=self.host_name, port=self.port, username=self.user, password=self.pwd)
                self.is_connect = True
            else:
                self.term = telnetlib.Telnet(host=self.host_name, port=self.port)
                self.is_connect = self._check_first_login()

            self.log(f'{self.host_name} : {self.port} 连接成功')
        except Exception as e:
            self.log(f'{self.host_name} : {self.port} {e} 连接失败')

        return self.is_connect

    def cmd_send(self, cmd, timeout=5):
        return_code, res = self._cmd_send(cmd, timeout)
        if return_code:
            return 1
        else:
            return res

    def _cmd_send(self, cmd, timeout):
        if not self.is_connect:
            return 1, None
        else:
            if self.host_type == 'ssh':
                _, out, err = self.term.exec_command(cmd, timeout=timeout)
                res = f"{''.join([_ for _ in out.readlines()])} {''.join([_ for _ in err.readlines()])}"
            else:
                self.term.write(f'{self.enter_char}'.encode('utf-8'))
                command_result = (self.term.read_until(self.login_head.encode('utf-8'),
                                                       timeout=timeout)).decode('utf-8')
                res = command_result.replace(f'{self.enter_char}{self.login_head}', '').reolace(f'{cmd}', '')
            self.log(res)
            return 0, res

    def close(self):
        self.term.close()
        self.is_connect = False


class Sftp:
    def __init__(self, host_name, port, user_name, password, host_type='ssh', quite=False):
        self.host_name = host_name
        self.port = port
        self.user_name = user_name
        self.password = password
        self.trans = paramiko.Transport(self.host_name, self.port)
        # self.trans = paramiko.Transport((self.host_name, self.port))
        self.sftp = None
        self.is_connected = False
        self.term = Terminal(self.host_name, self.user_name, self.password, self.port, host_type, quite)
        self.trans.connect(username=self.user_name, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(self.trans)

    def close_sftp(self):
        self.sftp.close()
        self.term.close()

    @staticmethod
    def path_walk(parent_path):
        """
        获得所有文件
        :param parent_path:  目录
        :return:
        """
        file_list = list()
        for _path, dirs, files in os.walk(parent_path):
            for file in files:
                file_list.append(os.path.join(_path, file))
        return file_list

    def _file_upload(self, local_path, remote_path):
        """
        上传文件
        :param local_path: 本地路径
        :param remote_path: 远程路径 + 文件
        :return:
        """
        remote_dir = os.path.dirname(remote_path)
        try:
            self.sftp.stat(remote_dir)
        except Exception as e:
            self.term.cmd_send('mkdir -p {}'.format(remote_dir))
        self.sftp.put(local_path, remote_path)

    def _folder_upload(self, local_folder, remote_folder, remote_os_type=0):
        """
        上传文件
        :param local_folder: 本地文件夹
        :param remote_folder: 远程文件夹
        :param remote_os_type: 系统型号 0 win 1 linux
        :return:
        """
        file_list = Sftp.path_walk(local_folder)
        for file in file_list:
            remote_filename = file.replace(local_folder, remote_folder)
            if remote_os_type:
                remote_filename = remote_filename.replace('\\', '/')
                remote_dir = os.path.dirname(remote_filename)
                try:
                    self.sftp.stat(remote_dir)
                except Exception:
                    # 递归创建目录 即使上级不存在 也会按目录层级创建目录
                    self.term.cmd_send('mkdir -p {}'.format(remote_dir))
            self.sftp.put(file, remote_filename)

    def remote_path_walk(self, _remote, files=[]):
        """
        加载sftp文件服务器对象（根目录）
        :param _remote: 远程文件夹
        :param files: 递归调用时 用于保存上一次文件
        :return:
        """
        files_list = self.sftp.listdir_attr(_remote)
        for file in files_list:
            tmp = f'{_remote}/{file.filename}'
            if stat.S_ISDIR(files.st_mode):
                self.remote_path_walk(tmp, files)
            else:
                files.append(tmp)
        return files

    def _folder_download(self, _remote, _local, local_os_type=0):
        """
        上传文件
        :param _local: 本地文件夹
        :param _remote: 远程文件夹
        :param remote_os_type: 系统型号 0 win 1 linux
        :return:
        """
        files = self.remote_path_walk(_remote)
        for file in files:
            local_file2write = file.replace(_remote, _local)
            if not local_os_type:
                local_file2write = local_file2write.replace('\\', '/')
            local_dir = os.path.dirname(local_file2write)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            self._file_download(file, local_file2write)

    def _file_download(self, _remote, _local):
        """

        :param _remote:
        :param _local:
        :return:
        """
        self.sftp.get(_remote, _local)

    def file_judge(self, args):
        """
        判断路径是否是文件（夹)
        :param args:
        :return:
        """
        if args.local:
            if os.popen(f'ls -l {args.local_path}').read():
                return 0 if os.path.isfile(args.local_path) else 1
            else:
                return -1
        else:
            res = self.term.cmd_send(f'ls -l {args.remote_path}')
            if res.startswith('total'):
                return 1
            elif res.startswith('-'):
                return 0
            else:
                return -1

    # TODO: 待添加上传下载验证是否成功
    def download(self, args):
        """

        :param args:
        :return:
        """
        _local = args.local_path  # 本地文件（夹）
        _remote = args.remote_path  # 远程文件（夹）
        local_os_type = args.local_os_type  # 系统型号 0 win 1 linux
        res = ''
        try:
            res = str(self.sftp.stat(_remote))
        except FileNotFoundError as e:
            print(f'{e} 没有找到这个文件（夹） {_remote}')
        if res.startswith('d'):
            self._folder_download(_remote, _local, local_os_type)
        elif res.startswith('-'):
            self._file_download(_remote, _local)
        else:
            print(f'{res}')
        self.close_sftp()
        return 0

    def upload(self, args):
        """
        sftp上传统一接口

        :return:
        """
        _local = args.local_path  # 本地文件（夹）
        _remote = args.remote_path  # 远程文件（夹）
        remote_os_type = args.remote_os_type  # 系统型号 0 win 1 linux

        if os.path.isdir(_local):
            self._folder_upload(_local, _remote, remote_os_type)
        else:
            self._file_upload(_local, _remote)
        self.close_sftp()
        return 0


def main():
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('host', help='')
    parent_parser.add_argument('-t', dest='type', required=False, default='ssh', choices=['ssh', 'telnet'], help='')
    parent_parser.add_argument('-u', dest='user', required=False, help='')
    parent_parser.add_argument('-p', dest='pwd', help='')
    parent_parser.add_argument('-p', dest='port', default=22, help='')
    parent_parser.add_argument('-q', dest='quiet', action='store_true', help='')
    parent_parser.add_argument('local_path', help='')
    parent_parser.add_argument('remote_path', help='')

    parent_parser.add_argument('-rt', dest='remote_os_type', required=False,
                               type=int, default=1, choices=[1, 0], help='系统型号 0 win 1 linux')
    parent_parser.add_argument('-lt', dest='local_os_type', required=False,
                               type=int, default=1, choices=[1, 0], help='系统型号 0 win 1 linux')

    parser = parent_parser.add_argument(description='Sftp tool...........')
    subparsers = parent_parser.add_argument(help='子命令使用方法')

    # 子命令 download
    parser_d = subparsers.add_parser('download', parents=[parent_parser],
                                     help='sftp_tool.py download host_ip -u user -p pwd local_path remote_path')
    # 子命令 upload
    parser_u = subparsers.add_parser('upload', parents=[parent_parser],
                                     help='sftp_tool.py download host_ip -u user -p pwd local_path remote_path')
    # 子命令 check
    parser_c = subparsers.add_parser('check', parents=[parent_parser],
                                     help='sftp_tool.py check host_ip -u user -p pwd local_path remote_path [-l]')
    parser_c.add_argument('-l', dest='local', action='store_true', defalut=False, help='local flag')
    args = parser.parse_args()

    try:
        host_type = args.type
        host = args.host
        user = args.user
        pwd = args.pwd
        port = args.port

        sftp = Sftp(host, port, user, pwd, host_type, args.quie )
        parser_d.set_defaults(function=sftp.download)
        parser_d.set_defaults(function=sftp.upload)
        parser_d.set_defaults(function=sftp.file_judge)
        args = parser.parse_args()
        res = args.fun(args)
        print(res)
        return res
    except AttributeError:
        print('执行sftp_tool.py -h 获取帮助')
main()
