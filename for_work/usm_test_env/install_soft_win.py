#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zhouey
@file: install_soft_win.py
@time: 2021/6/4 15:11
"""
import winrm
import subprocess
import platform
import time
import os

LOG = None


def init_log():
    '''
    初始化一个log 对象
    :return:
    '''
    import logging
    logger = logging.getLogger('LOG')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.FileHandler(filename='win_install.log')
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    ch1 = logging.StreamHandler()
    logger.addHandler(ch1)

    global LOG
    LOG = logger


def exec_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode == 3:
        return p.returncode, stdout
    if p.returncode != 0:
        return p.returncode, stderr
    return p.returncode, stdout


def exec_cmd_with_log(cmd):
    start_time = time.time()
    LOG.info('begin execution....')
    LOG.info(cmd)
    code, out = exec_cmd(cmd)
    if code != 0:
        LOG.info('execution failed ....')
        LOG.info('code={},out={}'.format(code, out.decode('utf-8')))
        return code, out.decode('utf-8')
    LOG.info('code={},out={}'.format(code, out.decode('utf-8')))
    LOG.info('the execution is complete,It takes {:.2f}'.format(time.time() - start_time))
    return code, out.decode('utf-8')


def connect_test():
    import winrm
    wintest = winrm.Session('http://10.0.6.177:5985/wsman', auth=('administrator', '1qaz@WSX'))
    ret = wintest.run_cmd('ipconfig')
    print(ret)
    print(ret.std_out.decode('gbk'))


def win_download(s_path, d_path):
    wintest = winrm.Session('http://10.0.6.177:5985/wsman', auth=('administrator', '1qaz@WSX'))

    cmd_str = 'if not exist c:\\tmp md c:\\tmp'

    ret = wintest.run_cmd(cmd_str)
    LOG.info(ret.std_out.decode('gbk'))

    cmd = "powershell (new-object Net.WebClient).DownloadFile('{}','{}')".format(s_path, d_path)
    print(cmd)
    ret = wintest.run_cmd('cd c:/tmp && {}'.format(cmd))
    print(ret.std_out.decode('gbk'))
    LOG.info(ret.std_out.decode('gbk'))


def stop_http_server():
    cmd_str = "ps -ef | grep 'python3 -m http.server' | grep -v grep | cut -c 9-15 |xargs kill -9"
    exec_cmd_with_log(cmd_str)


def start_http_server():
    cmd_str = "ps -ef | grep 'python3 -m http.server' | grep -v grep | wc -l"
    code, out = exec_cmd_with_log(cmd_str)
    print(out.split())
    if out.strip() != '1':
        LOG.info('start http server !!!!!')

        cmd_str = 'cd /home/soft_tool; nohup python3 -m http.server &'
        os.system(cmd_str)


def main():
    init_log()
    start_http_server()
    s_url = 'http://10.0.1.220:8000/win/python-3.6.7.exe'
    d_path = 'c:/tmp/python-3.6.7.exe'
    win_download(s_url, d_path)


if __name__ == '__main__':
    main()
    # connect_test()
    # init_log()
    # start_http_server()
