#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/17 17:44
# @Author  : v_bkaiwang
# @File    : stfp.py
# @Software: win10 Tensorflow1.13.1 python3.6.3

import os
import stat
import sys
import paramiko

sys.path.append((os.path.dirname((os.path.abspath('__file__')))).split("Lib")[0])
from GlobalConfig.global_config import TermCfg
from Lib.ComminLib.BaseLib.log_message import LogMessage, LOG_ERROR
from Lib.ComminLib.BaseLib.terminal import Terminal


class Sftp:
    def __init__(self, host_name, port, user_name, password,
                 proxy=False, proxy_ip=TermCfg.GLB_PROXY_HOST,
                 proxy_port=TermCfg.GLB_PROXY_PORT, proxy_username=TermCfg.GLB_PROXY_USER,
                 proxy_password=TermCfg.GLB_PROXY_PWD):

        self.host_name = host_name
        self.port = port
        self.user_name = user_name
        self.password = password

        self.proxy = proxy
        self.proxy_ip = proxy_ip
        self.proxy_port = proxy_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password

        self.is_connected = False
        if proxy:
            self.trans = paramiko.Transport(host_name, proxy_port)
            self.trans.connect(username=proxy_username, password=proxy_password)
            self.sftp = paramiko.SFTPClient.from_transport(self.trans)
            self.term = Terminal(host_type='ssh', host_ip=proxy_ip, port=proxy_port, username=proxy_username,
                                 password=proxy_password)

        else:
            self.trans = paramiko.Transport(host_name, port)
            self.trans.connect(username=proxy_username, password=password)
            self.sftp = paramiko.SFTPClient.from_transport(self.trans)
            self.term = Terminal(host_type='ssh', host_ip=proxy_ip, port=proxy_port, username=user_name,
                                 password=password)
            self.term.connect()
            self.tmp_dir = '/home/mtest/tmp'
            if self.proxy:
                self.tool_exist_check()

    def close_stfp(self):
        self.sftp.close()
        self.term.close()

    @staticmethod
    def path_walk(parent_path):
        """
        3# ??????????????????????????????
        :param parent_path: ??????
        :return: list
        """
        file_list = list()
        for _path, dirs, flies in os.walk(parent_path):
            for file in flies:
                file_list.append(os.path.join(_path, file))
        return file_list

    def _file_upload(self, local_path, remote_path):
        """
        ????????????
        :param local_path: ???????????? + ??????
        :param remote_path: ???????????? + ??????
        :return:
        """
        remote_dir = os.path.dirname(remote_path)
        try:
            self.sftp.stat(remote_dir)
        except Exception as e:
            # ?????????????????? ??????????????????????????? ????????????????????????
            self.term.cmd_send('mkdir -p {}'.format(remote_dir))
        self.sftp.put(local_path, remote_path)

    def _folder_upload(self, local_folder, remote_folder, remote_os_type=0):
        """
        ????????????
        :param local_folder: ????????????
        :param remote_folder: ????????????
        :param remote_os_type:
        :return: ???????????????
        """
        file_list = Sftp.path_walk(local_folder)
        # ????????????
        for file in file_list:
            remote_filename = file.replace(local_folder, remote_folder)
            if remote_os_type:
                remote_filename = remote_filename.replace('\\', '/')
                remote_dir = os.path.dirname(remote_filename)
                try:
                    self.sftp.stat(remote_dir)
                except Exception as e:
                    # ?????????????????? ??????????????????????????? ????????????????????????
                    self.term.cmd_send('mkdir -p {}'.format(remote_dir))
            self.sftp.put(file, remote_filename)

    def remote_path_walk(self, _remote, files=[]):
        """
        ??????stfp?????????????????????
        :param _remote: ????????????
        :param file: ??????????????? ???????????????????????????
        :return:
        """
        files_list = self.sftp.listdir_attr(_remote)
        for file in files_list:
            tmp = f'{_remote}/{file.filename}'
            if stat.S_ISDIR(file.st_mode):
                self.remote_path_walk(tmp, files)
            else:
                file.append(tmp)
        return files

    def _folder_download(self, _remote, _local, local_os_type=0):
        """

        :param _remote:???????????????
        :param _local:???????????????
        :param local_os_type:???????????????
        :return:
        """
        files = self.remote_path_walk(_remote)
        for file in files:
            local_file2write = file.replace(_remote, _local)
            if not local_os_type:
                local_file2write = local_file2write('\\', '/')
            local_dir = os.path.dirname(local_file2write)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            self._file_download(file, local_file2write)

    def _file_download(self, _remote, _local):
        """
        ????????????
        :param _remote:
        :param _local:
        :return:
        """
        self.sftp.get(_remote, _local)

    def tool_exist_check(self):
        """

        :return:
        """
        res = self.term.cmd_send('which sftp_tool.py')['rettxt']
        if 'which: no' in res:
            tool_path = '/usr/bin/sftp_tool.py'
            self._upload('sftp_tool.py', tool_path, remote_os_type=1)
            self.term.cmd_send(f'chmod +x {tool_path}')

    def _download_with_proxy(self, _remote, _local, local_os_type, quiet):
        """
        ??????????????????????????? ???self.tmp_dir??????????????????
        :param _remote:
        :param _local:
        :param local_os_type:
        :param quiet:
        :return:
        """
        cmd = f'sftp_tool.py check {self.host_name} -u {self.user_name} -p {self.password} {_local} {_remote}'
        cmd += ' -q' if quiet else ''
        res = int(self.term.cmd_send(cmd)['rettxt'])
        if not res:
            self.tmp_dir += f'/{os.path.basename(_remote)}'
        cmd = f'sftp_tool.py download {self.host_name} -u {self.user_name} -p {self.password} {self.tmp_dir} {_remote}'
        if quiet:
            cmd += ' -q'
        self.term.cmd_send(cmd)
        # DUT((_remote) -> ????????? (self.tmp_dir))
        cmd = f'sftp_tool.py download {self.host_name} -u {self.user_name} -p {self.password} {self.tmp_dir} {_remote}'
        if quiet:
            cmd += ' -q'
        self.term.cmd_send(cmd)
        # ?????????(self.tmp_dir -> ?????? (local))
        self._download(self.tmp_dir, _local, local_os_type)
        # ??????self.tmp_dir+??????????????????
        self.term.cmd_send(f'rm -rf {self.tmp_dir}/*')

    def _upload_with_proxy(self, _remote, _local, remote_os_type, quiet):
        # ??????(local) -> ?????????(self.tmp_dir))
        if os.path.isfile(_local):
            self.tmp_dir += f'/{os.path.basename(_local)}'
        self._upload(_local, self.tmp_dir, remote_os_type)
        # ?????????(self.tmp_dir) -> DUT(_remote))
        cmd = f'sftp_tool.py upload {self.host_name} -u {self.user_name} -p {self.password} {self.tmp_dir} {_remote}'
        if quiet:
            cmd += ' -q'
        self.term.cmd_send(cmd)
        # ??????self.tmp_dir+??????????????????
        self.term.cmd_send(f'rm -rf {self.tmp_dir}/*')

    def _download(self, _remote, _local, local_os_type):
        """
        stfp???????????????
        :param _remote:
        :param _local:
        :param local_os_type:
        :return:
        """
        res = ''
        try:
            res = str(self.sftp.stat(_remote))
        except FileNotFoundError as e:
            LogMessage(level=LOG_ERROR, module='Sftp', msg=f'{e} ????????????????????????/?????????')
        if res.startswith('d'):
            self._folder_download(_remote, _local, local_os_type)
        elif res.startswith('-'):
            self._file_download(_remote, _local)
        else:
            LogMessage(level=LOG_ERROR, module='Sftp', msg={res})
        return self.sftp.close()

    def _upload(self, _remote, _local, remote_os_type):
        """
        stfp???????????????
        :param _remote:
        :param _local:
        :param remote_os_type:
        :return:
        """
        if os.path.isdir(_local):
            self._folder_upload(_remote, _local, remote_os_type)
        else:
            self._file_upload(_remote, _local)

    def download(self, _remote, _local, local_os_type=0, quiet=True):
        if self.proxy:
            self._download_with_proxy(_remote, _local, local_os_type, quiet)
        else:
            self._download(_remote, _local, local_os_type)
        self.close_stfp()

    def upload(self, _remote, _local, local_os_type=0, quiet=True):
        if self.proxy:
            self._upload_with_proxy(_remote, _local, local_os_type, quiet)
        else:
            self._upload(_remote, _local, local_os_type)
        self.close_stfp()


if __name__ == '__main__':
    pass
