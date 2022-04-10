#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/4/10 23:58
# @Author  : v_bkaiwang
# @File    : send_qq_msg.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import os
import win32gui
import win32com.client
import win32con
import win32clipboard as w
import pythoncom


class sendMsg():
    def __init__(self, receiver, msg):
        self.receiver = receiver
        self.msg = msg
        self.setText()

    # 设置剪贴版内容
    def setText(self):
        w.OpenClipboard()
        w.EmptyClipboard()
        w.SetClipboardData(win32con.CF_UNICODETEXT, self.msg)
        w.CloseClipboard()

    # 发送消息
    def sendmsg(self):
        qq = win32gui.FindWindow(None, self.receiver)
        print(qq)
        if qq == 0:
            print("未找到聊天窗口")
            return
        try:
            pythoncom.CoInitialize()
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            win32gui.SetForegroundWindow(qq)
        except Exception as e:
            print(e)
        win32gui.SendMessage(qq, win32con.WM_PASTE, 0,
                             0)  # win32on 见site-packages\win32\lib\win32con.py,有的博文里出现的770对用的就是win32con.WM_PASTE
        win32gui.SendMessage(qq, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)


if __name__ == '__main__':
    # receiver = '千秋索'
    # receiver = '来不及忧伤'
    # receiver = '新版C3系统测试群'
    import time
    time.sleep(1)
    receiver = os.environ.get('receiver')
    print(receiver)
    msg = os.environ.get('msg')
    print(msg)
    # receiver = '来不及忧伤'
    # msg = '测试eee'
    qq = sendMsg(receiver, msg)
    qq.sendmsg()

