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
import sys

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


class InstallWinSoft():
    def __init__(self, ip, username, passwd):
        self.ip = ip
        self.username = username
        self.passwd = passwd
        self.wintest = winrm.Session('http://{}:5985/wsman'.format(self.ip), auth=(self.username, self.passwd))

    def init_winrm(self):
        return self

    def win_download(self, s_path, d_path):
        # bat shell
        cmd_str = 'if not exist c:\\tmp md c:\\tmp'

        ret = self.wintest.run_cmd(cmd_str)
        LOG.info(ret.std_out.decode('gbk'))

        cmd = "powershell (new-object Net.WebClient).DownloadFile('{}','{}')".format(s_path, d_path)
        LOG.info(cmd)

        ret = self.wintest.run_cmd('cd c:/tmp && {}'.format(cmd))
        LOG.info(ret.std_out.decode('gbk'))

        # ret = self.wintest.run_cmd('ipconfig /all')
        # LOG.info(ret.std_out.decode('gbk'))

    def install_python(self, pythonname='python-3.6.7.exe'):
        '''
        安装python环境，并初始化pip和安装第三方python 包
        :param pythonname: python 包名
        :return:
        '''
        cmd_str = 'if exist "c:\\tmp\\{}" (echo ok) else (echo err)'.format(pythonname)
        ret = self.wintest.run_cmd(cmd_str)
        value = ret.std_out.decode('gbk').strip()
        print(value)
        if value == 'err':
            LOG.info('{} is not exist,exit -1'.format(pythonname))
            exit(-1)

        LOG.info('install {}'.format(pythonname))
        install_cmd = '{} /quiet InstallAllUsers=1 PrependPath=1 ' \
                      'Include_test=0 TargetDir=c:\python3'.format(pythonname)
        ret = self.wintest.run_cmd('cd c:\\tmp && {}'.format(install_cmd))
        if ret.status_code == 0:
            LOG.info('{} install sucess....'.format(pythonname))
        else:
            LOG.info(ret)

        self._conf_pip_sourcce()
        self._pip_install_pack()

    def _conf_pip_sourcce(self):
        # 配置python 源
        LOG.info(sys._getframe().f_code.co_name)

        cmd_str = 'if not exist C:\\Users\Administrator\pip md C:\\Users\Administrator\pip'
        ret = self.wintest.run_cmd(cmd_str)
        LOG.info(ret)

        cmd_str_list = ['echo [global] > C:\\Users\Administrator\pip\pip.ini ',
                        'echo timeout = 6000 >> C:\\Users\Administrator\pip\pip.ini',
                        'echo index-url =https://pypi.tuna.tsinghua.edu.cn/simple >> C:\\Users\Administrator\pip\pip.ini',
                        'echo [install] >> C:\\Users\Administrator\pip\pip.ini',
                        'echo trusted-host=pypi.tuna.tsinghua.edu.cn >> C:\\Users\Administrator\pip\pip.ini']

        for cmd_str in cmd_str_list:
            ret = self.wintest.run_cmd(cmd_str)
            print(ret)

    def _pip_install_pack(self):
        cmd_str_list = ['pip install pywinauto']
        for cmd_str in cmd_str_list:
            LOG.info('runcmd {}'.format(cmd_str))
            ret = self.wintest.run_cmd(cmd_str)
            if ret.status_code == 0:
                LOG.info('install sucess...')
            else:
                LOG.info(ret)

    def install_bandzip(self):
        '''
        安装解压软件
        :return:
        '''
        s_path = 'http://10.0.1.220:8000/win/BANDIZIP-SETUP.EXE'
        d_path = 'c:/tmp/BANDIZIP-SETUP.EXE'
        self.win_download(s_path, d_path)
        cmd_str = 'BANDIZIP-SETUP.EXE /auto'
        ret = self.wintest.run_cmd('cd c:\\tmp && {}'.format(cmd_str))
        if ret.status_code == 0:
            LOG.info('install BANDIZIP sucess...')
        else:
            LOG.info(ret)

    def install_king(self):
        # 金仓7 客户端 kdb-7-win.zip
        s_path = 'http://10.0.1.220:8000/win/kdb-7-win.zip'
        d_path = 'c:/tmp/kdb-7-win.zip'
        # 下载
        LOG.info('download kdb-7-win')
        self.win_download(s_path, d_path)
        # 解压
        LOG.info('unzip kdb-7-win')
        cmd_str = 'Bandizip.exe bx -y -o:c:\\tmp\\kdb-7  C:\\tmp\\kdb-7-win.zip'
        ret = self.wintest.run_cmd('cd C:\Program Files\Bandizip && {} '.format(cmd_str))
        if ret.status_code == 0:
            LOG.info('unzip kdb-7-win.zip  to kdb-7 sucess...')
        else:
            LOG.info(ret)


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


def init_remote_env(ip, username, passwd):
    '''
    初始化win远程机的环境
    python
    :return:
    '''
    install = InstallWinSoft(ip, username, passwd)

    # 初始化pyton3.6.7 环境
    s_url = 'http://10.0.1.220:8000/win/python-3.6.7.exe'
    d_path = 'c:/tmp/python-3.6.7.exe'
    install.win_download(s_url, d_path)
    install.install_python()
    install.install_bandzip()

    # install.install_king()


def init_local_env():
    '''
    初始化本地linux服务器环境,此处跳板机也是本地安装包服务器环境
    :return:
    '''
    init_log()
    start_http_server()


def main():
    init_local_env()

    ip = '10.0.6.177'
    username = 'administrator'
    passwd = '1qaz@WSX'
    init_remote_env(ip, username, passwd)


if __name__ == '__main__':
    main()
