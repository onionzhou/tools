#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zhouey
@file: 1.py
@time: 2021/5/10 16:37
"""

import paramiko
import time
LOG = None


def test():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='10.0.1.132', port=22, username='root', password='475869@hjl.cn')

    cmd_list = ['ls', 'sleep 5', 'ip -a ']
    for cmd in cmd_list:
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        print(stdout.read())
        print(stderr.read())
    ssh.close()


def loger_test():
    import logging

    # create logger
    logger = logging.getLogger('LOG')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch1 = logging.FileHandler(filename='test.log')
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    logger.addHandler(ch1)

    # 'application' code
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')
    global LOG
    LOG = logger


def winrm_test():
    import winrm
    wintest = winrm.Session('http://10.0.1.122:5985/wsman', auth=('administrator', '1qaz@WSX'))
    cmd_str="powershell (new-object System.Net.WebClient).DownloadFile('http://10.0.1.220:8000/USM.txt','C:\\Users\Administrator\Downloads\jwt1')"
    ret = wintest.run_cmd(cmd_str)
    # ret = wintest.run_cmd('ipconfig')
    print(ret)
    print(ret.std_out.decode('gbk'))


if __name__ == '__main__':
    # test()
    # loger_test()
    # LOG.debug('asdasdasdas')
    winrm_test()
