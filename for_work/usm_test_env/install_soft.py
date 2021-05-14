#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zhouey
@file: install_soft.py
@time: 2021/5/10 17:41
"""
import platform
import subprocess
import time
import pexpect
import sys
import argparse

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
    ch = logging.FileHandler(filename='install.log')
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


def check_os():
    ret = platform.system()
    if ret == 'Windows':
        LOG.info('this is windows ')
    elif ret == 'Linux':
        LOG.info('linux')
    else:
        LOG.info('not support os !!')
        exit(-1)


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
        LOG.info('code={},out={}'.format(code,out.decode('utf-8')))
        exit(-1)
    LOG.info('the execution is complete,It takes {:.2f}'.format(time.time() - start_time))


def install_docker():
    cmd_list = ['curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun',
                'yum install -y yum-utils device-mapper-persistent-data lvm2',
                'yum-config-manager --add-repo \
                  https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/centos/docker-ce.repo',
                'yum install docker-ce docker-ce-cli containerd.io'
                ]

    for cmd_str in cmd_list:
        exec_cmd_with_log(cmd_str)


def modify_mysql_conf():
    ''' 交互式命令方式修改mysql配置
        修改mysql root 密码存储方式为 mysql_native_password
    '''
    LOG.info('#######################<modify_mysql_conf>#####################################')
    child = pexpect.spawn("docker exec -it mysql_v8.0.24 bash -c 'mysql -u root -h 127.0.0.1 --password=123456'")
    # child.expect(pexpect.EOF)
    # fout = open('modify_mysql.log', 'ab')
    child.logfile = sys.stdout
    # child.logfile = fout

    mysql_cmd_list = [
        'use mysql;',
        "ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY '123456';",
        'FLUSH PRIVILEGES;',
        'exit;'
    ]

    for cmd in mysql_cmd_list:
        LOG.info('cmd: {}'.format(cmd))
        # time.sleep(1)
        child.expect('mysql>')
        child.sendline(cmd)

    child.expect('~]#')
    # fout.close()
    child.close()


def install_mysql():
    cmd_str = 'systemctl  status  docker'
    code, out = exec_cmd(cmd_str)
    if code == 3:
        LOG.info('start docker .......')
        LOG.info(cmd_str)
        code, out = exec_cmd('systemctl start docker')
        LOG.info(code, out.decode('utf-8'))
    elif code == 0:
        LOG.info('docker has started')

    cmd_list = ['docker pull mysql:8.0.24 ',
                'docker run -itd --name mysql_v8.0.24 -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql']

    for cmd_str in cmd_list:
        exec_cmd_with_log(cmd_str)

    LOG.info('sleeping 30s,waiting docker run mysql... ')
    time.sleep(30)
    modify_mysql_conf()


def main():
    import sys

    init_log()

    code, err = exec_cmd('docker -v')
    if code == 0:
        LOG.info('docker installed....')
    else:
        install_docker()

    soft_list = sys.argv[1:]
    LOG.info('install soft {}'.format(soft_list))

    # 安装mysql
    for soft in soft_list:
        if soft == 'mysql_v8.0.24':
            LOG.info('install soft mysql_v8.0.24...')
            install_mysql()
        elif soft == 'telnet':
            LOG.info('install soft telnet...')


if __name__ == '__main__':
    # yum install python3 -y
    # pip3 install pexpect
    main()
