#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/5 23:27
# @Author  : v_bkaiwang
# @File    : env_version.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
from time import sleep, time
from GlobalConfig.global_config import ENVS_, PROXY_SZ
from Lib.CommonLib.BaseLib.log_message import LogMessage, LOG_SYS, LOG_ERROR
from Lib.CommonLib.BaseLib.terminal import Terminal
from Lib.CommonLib.CoreLib.msg_center import MsgCenter
import os

MODULE_NAME = os.path.splitext(os.path.basename(__file__))[0]
MsgCenter(MODULE_NAME)
PKG_DIR_PATH = '/var/version/version_tools_asic'


class EnvVersion:
    def __init__(self, agent: Terminal, ap_ssh: Terminal, bmc_ssh: Terminal):
        self.agent = agent
        self.term_ap = ap_ssh
        self.term_bmc = bmc_ssh
        self.connect_time = 10

    def sys_up_data(self, version_path):
        self.agent.connect()
        tar_file_path, bin_file_path, rpm_file_path = self._get_version_file(version_path)
        if tar_file_path:
            bmc_version = self._update_bmc(tar_file_path)
            LogMessage(level=LOG_SYS, module=MODULE_NAME, msg=f"bmc update to {bmc_version}")

        if bin_file_path:
            bios_version = self._update_bios(bin_file_path)
            LogMessage(level=LOG_SYS, module=MODULE_NAME, msg=f"bios update to {bios_version}")

        if rpm_file_path:
            os_version = self._update_os(rpm_file_path)
            LogMessage(level=LOG_SYS, module=MODULE_NAME, msg=f"os update to {os_version}")

    def _update_bmc(self, tar_path):
        self.agent.cmd_send(f'cd {PKG_DIR_PATH}')
        cmd = f'curl -k -u {self.term_bmc.term.username}:{self.term_bmc.term.password} -X POST https://{self.term_bmc.host_ip}/redfish/v1/UpdateService --data--binary "@{tar_path}"'
        self.agent.cmd_send(cmd=cmd, timeout=60)
        cmd = f'impitool -H {self.term_bmc.host_ip} -U {self.term_bmc.term.username} -P {self.term_bmc.term.password} -I lanplus mc reset cold'
        self.agent.cmd_send(cmd=cmd, timeout=60)
        count = 0
        while (not self.term_bmc.connect()) and (count < self.connect_time):
            count += 1
            LogMessage(level=LOG_SYS, module=MODULE_NAME, msg=f"try connect bmc fail : {count}")
            sleep(30)
        return self._get_bmc_version()

    def _update_bios(self, bin_path):
        self.agent.cmd_send(f'ssh-keygen -R {self.term_bmc.host_ip}')
        cmd = f'scp {bin_path} {self.term_bmc.term.username}@{self.term_bmc.host_ip}:/tmp/bios.bin'
        self.agent.cmd_send(cmd=cmd, wait4ret_str=True, ret_str='yes/no)?')
        self.agent.cmd_send(cmd='yes', wait4ret_str=True, ret_str='password:')
        self.agent.cmd_send(cmd=self.term_bmc.term.password)
        # 要抄一下 bios-update.sh !!!
        self.term_bmc.connect()
        self.term_bmc.cmd_send(cmd='su', ret_str='Password:', wait4ret_str=True)
        self.term_bmc.cmd_send(cmd='0penBmc')
        self.term_bmc.cmd_send(cmd='bios-update.sh /tmp', ret_str='switch bios flash to host')
        self.term_bmc.cmd_send(cmd='impitool power off')
        self.term_bmc.cmd_send(cmd='impitool power on')
        count = 0
        while (not self.term_ap.connect()) and (count < self.connect_time):
            count += 1
            LogMessage(level=LOG_SYS, module=MODULE_NAME, msg=f"try connect ap fail : {count}")
            sleep(30)
        return self._get_bios_version()

    def _update_os(self, rpm_path):
        self.agent.cmd_send(f'ssh-keygen -R {self.term_bmc.host_ip}')
        rpm_pkg_name = os.path.basename(rpm_path)
        cmd = f'scp -r {rpm_path} {self.term_ap.term.username}@{self.term_ap.host_ip}:/tmp/{rpm_pkg_name}'
        self.agent.cmd_send(cmd=cmd, wait4ret_str=True, ret_str='yes/no)?')
        self.agent.cmd_send(cmd='yes', wait4ret_str=True, ret_str='password:')
        self.agent.cmd_send(cmd=self.term_bmc.term.password)
        """ap上的操作"""
        self.term_ap.connect()
        cmd = f'rpm -ivh --force /tmp/{rpm_pkg_name}'
        try:
            self.term_ap.cmd_send(cmd=cmd, timeout=2 * 60)
        except Exception as e:
            LogMessage(level=LOG_SYS, module=MODULE_NAME, msg=f"cmd send timeout : {e}")
        self.term_ap.cmd_send(cmd='reboot', quite=True)
        self.term_ap.close()

        count = 0
        while (not self.term_ap.connect()) and (count < self.connect_time):
            count += 1
            LogMessage(level=LOG_SYS, module=MODULE_NAME, msg=f"try connect ap fail : {count}")
            sleep(30)
        return self._get_os_version()

    def _get_bmc_version(self) -> str:
        res_txt = self.term_bmc.cmd_send('impitool mc info')['rettxt']
        for line in res_txt.splitlines():
            if 'Firmware Revision' in line:
                _, value = line.split(":")
                value = value.strip()
                return value
        return ''

    def _get_bios_version(self) -> str:
        res_txt = self.term_ap.cmd_send('dmidecode')['rettxt']
        for line in res_txt.splitlines():
            if 'Version' in line:
                _, value = line.split(":")
                value = value.strip()
                return value
        return ''

    def _get_os_version(self) -> str:
        res_txt = self.term_ap.cmd_send('cat /proc/version')['rettxt']
        os_version = res_txt.replace(res_txt[res_txt.find('('):res_txt.find('SMP') + 4], '')
        os_version = os_version.replace('Linux version', '').replace('.ali5000.alios7.aarch64', '')
        return os_version

    def _get_version_file(self, version_path):
        """解析文件"""
        res = self.agent.cmd_send(f'ls {version_path}')
        rpm_file_path = ''
        bin_file_path = ''
        tar_file_path = ''
        file_names = res['rettxt'].splitline()[0]
        for file_name in file_names:
            if '.tar' in file_name:
                tar_file_path = version_path + file_name
            if '.rmp' in file_name:
                rpm_file_path = version_path + file_name
            if '.bin' in file_name:
                bin_file_path = version_path + file_name
        return tar_file_path, bin_file_path, rpm_file_path

    def init_version_path(self, tar_path, rpm_path, bin_path):
        version_path = f'/tmp/EnvVersion_{int(time())}/'
        self.agent.cmd_send(f'mkdir {version_path}')
        self.agent.cmd_send(f'cp -r {tar_path} {version_path}')
        self.agent.cmd_send(f'cp -r {rpm_path} {version_path}')
        self.agent.cmd_send(f'cp -r {bin_path} {version_path}')
        return version_path


def main():
    t0 = time()
    agent = Terminal(**PROXY_SZ, timeout=5, hold=True)
    bmc_ssh = Terminal(**ENVS_['EVB_207_BMC_SSH'], timeout=5, hold=True)
    ap_ssh = Terminal(**ENVS_['EVB_207_HAPS_SSH'], timeout=5)
    tar_path = '/var/version/Evb/B112/bmc/*'
    rpm_path = '/var/version/Evb/B112/os/005/*'
    bin_path = '/var/version/Evb/B112/uefi/M1fipimage_B112.bin*'
    env = EnvVersion(agent, bmc_ssh, ap_ssh)
    version_path = env.init_version_path(tar_path, rpm_path, bin_path)
    EnvVersion(agent, bmc_ssh, ap_ssh).sys_up_data(version_path)
    print(time() - t0)


if __name__ == '__main__':
    main()
