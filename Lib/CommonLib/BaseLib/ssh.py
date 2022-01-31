#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/7 0:02
# @Author  : v_bkaiwang
# @File    : ssh.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
import re
import socket
import time
import paramiko

from GlobalConfig.globalconfig import TermCfg
from Lib.ComminLib.BaseLib.log_message import LogMessage, LOG_INFO, LOG_ERROR

class Ssh:
    def __init__(self, host_ip, port, username, password, timeout=5, proxy=False, proxy_ip=TermCfg.GLB_PROXY_HOST,
                 proxy_port=TermCfg.GLB_PROXY_PORT, proxy_username=TermCfg.GLB_PROXY_USER, input_interval=0.1,
                 proxy_password=TermCfg.GLB_PROXY_PWD, ret_str="", hold=False, called=False, enter_char=None,
                 view_mode='os'):
        self.proxy = proxy
        self.timeout = timeout
        self.is_connected = False
        # 创建一个ssh 客户端 连接服务器
        self.ssh = paramiko.SSHClient()
        # 加载创建的白名单
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 判断是否有代理 场景 ：跳转机刀执行机
        if self.proxy:
            self.proxy_ip = proxy_ip
            self.proxy_port = proxy_port
            self.proxy_username = proxy_username
            self.proxy_password = proxy_password

        self.hostname = host_ip
        self.port = port
        self.username = username
        self.password = password
        self.name = host_ip + ":" + str(port)

        self.enter_char = enter_char
        self.view_mode = view_mode
        self.default_buffer_size = 1024
        self.shell = None
        self.hold = hold  # 是否保持会话
        self.called = called  # call by telnet
        self.quiet = False

        self.scale_factor = TermCfg.GLB_SCALE_FACTOR
        self.ret_str = ret_str
        self.wait4ret_str = False
        self.login_head = ''  # 连接后的头部 一般与ret_str相同 登陆的用户@主机名 当前所在的目录:用户权限
        self.input_interval = input_interval * self.scale_factor
        self.delay_recv = 0  # 延迟接受返回值
        # VT100 ANSI转义序列字符串正则
        self.ansi_escape = re.compile(br'(?:\x1B[@-z\\-_]|[\x80=\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])',
                                      re.VERBOSE)

    @property
    def pattern(self):
        # TODO:易冲突 待完善 修改为用户名@hostname 目录正则形式
        return re.compile(rf'.*?{self.username}[@:]*.*?[\n]*[#$]|Shell|\w+:\\>')

    def connect(self):
        try:
            if self.proxy:
                # 创建代理客户端
                proxy_ssh = paramiko.SSHClient()
                proxy_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                proxy_ssh.connect(hostname=self.proxy_ip, username=self.proxy_username,
                                  password=self.proxy_password, timeout=self.timeout)
                LogMessage(level=LOG_INFO, module='Ssh',
                           msg=f'Connect to proxy{self.proxy_ip}: {str(self.proxy_port)} successfully!!')
                vm_transport = proxy_ssh.get_transport()
                remote_address = (self.hostname, self.port)
                local_address = (self.proxy_ip, self.proxy_port)
                vm_channel = vm_transport.open_channel("direct_tcpip", remote_address, local_address)

                self.ssh.connect(hostname=self.proxy_ip, username=self.username, sock=vm_channel,
                                 password=self.password, timeout=self.timeout)
            else:
                self.ssh.connect(hostname=self.proxy_ip, username=self.username, port=self.port,
                                 password=self.password, timeout=self.timeout)
            if self.hold:
                # 引用一个shell维持会话
                self.shell = self.ssh.invoke_shell(width=256)
            self.is_connected = True
            LogMessage(level=LOG_INFO, module='Ssh', msg=f'Connect to host {self.name} successfully!!')
        except Exception as e:

            LogMessage(level=LOG_ERROR, module='Ssh', msg=f'Failed to host {e} connect!!')
        # 切换英文打印
        if self.hold:
            try:
                if self.is_connected:
                    tmp_shell = self.ssh.invoke_shell()
                    tm_reshult = self._recv()
                    self.login_head = self.pattern.findall(tm_reshult)[0]
                    tmp_shell.close()
            except IndexError as e:
                LogMessage(level=LOG_ERROR, module='Ssh', msg=f'{e}')
            except AttributeError:
                LogMessage(level=LOG_ERROR, module='Ssh', msg=f'获取login_head失败')
        return self.is_connected

    def cmd_send(self, cmd, ret_str='', timeout=5, wait4ret_str=False, max_loop_time=3, quiet=False,
                 delay_recv=0):
        """

        :param cmd: 命令
        :param ret_str: 返回结果的字符串
        :param timeout: 超时
        :param wait4ret_str: {特殊场景 ret_str有值时 此参数才有意义！必须等待ret_str 才结束，此时login_head不生效}
        :param wait4ret_str:
        :param max_loop_time: hold/telnet模式下 循环等待命令接收完毕或者打满
        self.shell.recv()的buffer——size 延迟网络导致的超时问题
        :param quiet: 不打印日志
        :param delay_recv:
        :return:
        """
        # 延迟接收返回值，hold才生效
        if self.hold:
            self.delay_recv = delay_recv
        command_result = ""
        self.quiet = quiet
        if ret_str:
            self.ret_str = ret_str  # 将传入的 返回值结束字符串 赋值给成员变量
        self.wait4ret_str = wait4ret_str
        if not self.is_connected:
            LogMessage(level=LOG_ERROR, module='Ssh', msg=f'Ssh{self.name} is not connected ,Please check again')
            return command_result
        if self.called or self.hold:
            # called 为telnet调用 hold为ssh保持连接
            command_result = self._exec_command(cmd, timeout=timeout, buffer_size=self.default_buffer_size,
                                                max_loop_time=max_loop_time)
        else:
            if wait4ret_str:
                stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=timeout)
                # 不等返回值 执行命令后直接返回
            else:
                self.ssh.exec_command(cmd, timeout=timeout)
                return command_result

            for line in stderr.readlines():
                command_result += line

            for line in stdout.readlines():
                command_result += line
                # 如果ret_str存在 且ret_str 在command_result里 就退出
                if all([ret_str, ret_str in command_result]):
                    break
        return command_result

    def _exec_command(self, cmd, timeout, buffer_size, max_loop_time=3):
        """
        执行命令并返回 ssh_telnet ,ssh hould 模式不会采用此方法发
        :param cmd:
        :param timeout:
        :param buffer_size: 缓冲区大小 指定后 在self.shell.timeout的时间内
                            应该接收完毕 或者打满此空间否则 超过max_loop_time 后会报错，并关闭连接
        :param max_loop_time: hold/telnet模式下 循环等待命令接收完毕或者打满
        self.shell.recv()的buffer——size 延迟网络导致的超时问题
        :return:
        """
        for i in range(0, len(cmd), 20):
            self.shell.send(cmd[i:i + 20])
            time.sleep(self.input_interval)
        self.shell.send(self.enter_char)

        if self.delay_recv:
            time.sleep(self.delay_recv)
        # 获取返回值
        result = self._recv(buffer_size=buffer_size, timeout=timeout, max_loop_time=max_loop_time)
        if not isinstance(result, bool):
            # return 包含cmd和login head 在此剔除
            result = result.replace(cmd.strip(), '').replace(self.login_head, '').strip
        return result

    def _recv(self, buffer_size=None, timeout=None, max_loop_time=3):
        """

        :param buffer_size:
        :param timeout:
        :param max_loop_time:
        :return:
        """
        buffer_size = buffer_size if buffer_size else self.default_buffer_size
        timeout = timeout if timeout else self.timeout
        self.shell.timeout = timeout
        result = b''  # 最终结果
        ret_tmp = b''  # 如果不为‘’ 就break
        tmp_response = b''  # 临时的返回字节最大为1024
        increase_timeout = 1.5 * self.scale_factor  # 递增的临时timeout
        loop_time = 0  # 统计超时次数 于max loop time比较 退出循环
        last_res = b''
        while True:
            if self.view_mode in ['itos', 'uefi']:
                time.sleep(0.5 * self.scale_factor)
            try:
                tmp_response = self.shell.recv(buffer_size)
            except socket.timeout:
                self.shell.timeout = timeout * increase_timeout
                loop_time += 1
            # 用‘’ 替换ansi转义序列
            tmp_res = self.ansi_escape.sub(b'', tmp_response)

            if b'Connection refused' in tmp_res:
                """
                debug 有未关闭的残留链接 导致拒绝登录
                解决方法 关闭pycharm，git工具清除， 删除pycharm缓存 重新打开
                
                """
                LogMessage(level=LOG_ERROR, module="Ssh", msg='连接被拒绝 请排查原因')
                result = False
                break
            # 当返回值过大 会占用大量内存  导致pycharm在控制台输出log很久 调用cmd_send时 设置quiet=True
            # 取消日志打印

            # 并在此处用 窗口临时化
            if self.quiet:
                result = b''.join([last_res, tmp_res])
                last_res = tmp_res
            else:
                result += tmp_res
            # 当cmd_send传递到了ret_str时 在此判断到目前为止接受的返回值 是否存在ret_str
            if self.ret_str:
                ret_tmp = re.search(f'{self.ret_str}', result.decode('utf-8', errors='ignore'))

            # 当wait4ret_str = True时 login_head 在result 也不返回（特殊场景）
            if self.wait4ret_str:
                # return str 在 return才返回
                if ret_tmp:
                    break
            else:
                # 每次获取命令提示符 login_head
                tmp = self.pattern.search(result.decode('utf-8', errors='ignore'))
                # 如果当前在result里 匹配到reyurn str 或者 login_head 就退出接受

                if tmp or ret_tmp:
                    if tmp:
                        self.login_head = tmp.group()
                    # 读写安全寄存器出现异常
                    if ret_tmp and "Exception" in self.ret_str:
                        return False
                    break
            if loop_time == max_loop_time:
                break
        return result if isinstance(result, bool) else result.decode('utf-8', errors='ignore')

    def msg_read(self, timeout):
        # 回读信息
        ret = ''
        t_total = 0
        t_step = 0.5

        if not self.is_connected:
            LogMessage(level=LOG_ERROR, module='Ssh', msg=f'Ssh{self.name} is not connected ,Please check again')
            return ret
        while True:
            stdin, stdout, stderr = self.ssh.exec_command(self.enter_char, timeout=timeout)
            ret += stdout.readlines()
            LogMessage(level=LOG_INFO, module='Ssh', msg=stdout.readlines())
            time.sleep(t_step)
            t_total = t_total + t_step
            if t_total < timeout:
                continue
            else:
                break

    def close(self):
        if self.is_connected:
            try:
                self.ssh.close()
                if self.shell:
                    self.shell.close()
                self.is_connected = False
                LogMessage(level=LOG_INFO, module='Ssh', msg=f'SSH {self.name} is close')
            except Exception as e:
                LogMessage(level=LOG_INFO, module='Ssh', msg=f'SSH {self.name} close failed, error info {e}')

    def lang2us(self):
        """
        ssh 切换英文打印
        :return:
        """
        self.cmd_send(cmd='LANG="en_US"', ret_str="")
        self.cmd_send(cmd='LANGUAGE="en_US"', ret_str="")
        self.cmd_send(cmd='SUPPORTED="zh_CN.GB18030:zh_CN:zh:en_US.UTF-8:en_US:en"', ret_str="")
        self.cmd_send(cmd='SYSFONT="lat0_sun16"', ret_str="")
        self.cmd_send(cmd='SYSFONTACM="8859-15"', ret_str="")


if __name__ == '__main__':
    pass






