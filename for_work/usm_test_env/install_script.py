#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zhouey
@file: install_script.py
@time: 2021/6/7 14:52
安装脚本测试
"""

import os

from time import sleep


def install_king_7():
    from pywinauto import Application
    cmd_str = 'C:\\tmp\kdb-7\setup.bat'
    os.system(cmd_str)

    while True:
        try:
            app = Application().connect(title="金仓数据库 KingbaseES V7 安装程序", class_name='SunAwtFrame')
            print('连接成功.....')
            break
        except:
            print('wait 连接安装程序，sleep 30s')
            sleep(30)

    app.window(title="金仓数据库 KingbaseES V7 安装程序")

    app = Application().connect(title_re=".*金仓数据库 KingbaseES V7 安装程序.*")
    # app.window(title="金仓数据库 KingbaseES V7 安装程序", class_name="SunAwtFrame").print_control_identifiers()

    app.window(title="金仓数据库 KingbaseES V7 安装程序", class_name="SunAwtFrame").type_keys('{ENTER}')
    # 4下
    for _ in range(4):
        app.window(title="金仓数据库 KingbaseES V7 安装程序", class_name="SunAwtFrame").type_keys('{TAB}')

    app.window(title="金仓数据库 KingbaseES V7 安装程序", class_name="SunAwtFrame").type_keys('{SPACE}')
    # 4下
    for _ in range(4):
        app.window(title="金仓数据库 KingbaseES V7 安装程序", class_name="SunAwtFrame").type_keys('{TAB}')

    for _ in range(3):
        app.window(title="金仓数据库 KingbaseES V7 安装程序", class_name="SunAwtFrame").type_keys('{ENTER}')


def ssh_connect():
    import paramiko
    ip = '10.0.1.132'
    port = 22
    username = 'root'
    password = '123456'
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(ip, port, username, password,allow_agent=False,)
    print('------------')
    stdin, stdout, stderr = s.exec_command('ls')

    print(stdout.read().decode('utf-8'))


if __name__ == '__main__':
    # install_king_7()
    ssh_connect()
