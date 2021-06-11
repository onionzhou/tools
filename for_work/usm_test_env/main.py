#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zhouey
@file: main.py
@time: 2021/5/13 16:46
自动化部署主函数
"""

import paramiko
import os
import yaml
import time

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
    ch = logging.FileHandler(filename='exec.log')
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    ch1 = logging.StreamHandler()
    logger.addHandler(ch1)
    # add ch to logger
    logger.addHandler(ch)
    global LOG
    LOG = logger


def read_yaml_to_json(yaml_file=""):
    try:
        if not yaml_file:
            yaml_file = os.path.join(os.path.dirname(__file__), "config.yaml")
        with open(yaml_file, 'r', encoding="utf-8") as f:
            conf = yaml.load(f, Loader=yaml.FullLoader)
            return conf
    except Exception as e:
        print(e)
        raise Exception("读取 yaml 配置文件 为 Json 失败.")


class RemoteLoginApi():
    def __init__(self, ip, port, username, passwd):
        self.ip = str(ip)
        self.port = port
        self.username = username
        self.passwd = passwd

    def connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        count = 0
        while True:
            try:
                self.ssh.connect(hostname=self.ip, port=self.port, username=self.username, password=self.passwd)
                break
            except Exception as e:
                LOG.info('connect failed , sleep 1s ,reconnect.....')
                LOG.info(e)
                time.sleep(1)
                count += 1
            if count == 5:
                LOG.info('reconnect {},connect failed ....'.format(count))
                exit(-1)

        self.sftp = self.ssh.open_sftp()

        return self

    def exec_cmd(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd, get_pty=True)
        # LOG.info(stdout.read().decode('utf-8'))
        # LOG.info(stderr.read().decode('utf-8'))
        status_code = stdout.channel.recv_exit_status()
        out = stdout.read().decode('utf-8')
        err = stderr.read().decode('utf-8')
        return status_code, out, err

    def upload_file(self, local_path, remote_path):
        ret = self.sftp.put(local_path, remote_path, confirm=True)
        LOG.info(ret)

    def download_file(self, remote_path, local_path):
        ret = self.sftp.get(remote_path, local_path)
        LOG.info(ret)


def init_env(ip,port,username,passwd,soft_list):
    # ip = '10.0.1.132'
    # port = 22
    # username = 'root'
    # passwd = '475869@hjl.cn'

    LOG.info('{}--{}--{}--{}--{}'.format(ip, port, username, passwd, soft_list))
    LOG.info('{}--{}--{}--{}--{}'.format(type(ip), type(port), type(username), type(passwd), type(soft_list)))

    soft_str=' '.join(soft_list)
    print(soft_str)
    client = RemoteLoginApi(ip, port, username, passwd)
    client.connect()

    print('connect sucess!!!')
    code, out, err = client.exec_cmd('python3 -V')
    if code == 0:
        LOG.info('python3 installed..')
        LOG.info(out)

    else:
        cmd_list = ['yum install python3 -y', 'pip3 install pexpect']
        for cmd in cmd_list:
            LOG.info('exce "{}".....'.format(cmd))
            code, out, err = client.exec_cmd(cmd)
            if code == 0:
                LOG.info('cmd exce ok....')
            else:
                LOG.info(out)
                LOG.info(err)
                exit(-1)
    # 上传软件

    local_path = os.path.join(os.getcwd(), 'install_soft.py')
    client.upload_file(local_path, '/root/install_soft.py')

    code, out, err = client.exec_cmd('python3 /root/install_soft.py {}'.format(soft_str))
    if code == 0:
        LOG.info('python3 /root/install_soft.py {}'.format(soft_str))
        LOG.debug(out)
    else:
        LOG.info(code)
        LOG.info(out)
        LOG.info(err)
    log_local_path = os.path.join(os.getcwd(), 'install.log')
    client.download_file('/root/install.log', log_local_path)


if __name__ == '__main__':
    init_log()
    # init_env()
    conf = read_yaml_to_json()
    print(conf.get('linux'))
    host_list = conf.get('linux').get('hosts')
    for host in host_list:
        ip = host.get('ip')
        port = host.get('port')
        user = host.get('user')
        passwd = host.get('passwd')
        soft_list = host.get('softname')
        print(ip,port,user,passwd,soft_list)
        init_env(ip,port,user,passwd,soft_list)

