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
import threading
from scripts.zabbix_api import add_host_to_zabbix_server
from scripts.zabbix_api import del_host_from_zabbix_server

LOG = None

SOFT_PATH = None


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
        raise Exception("读取 yaml 配置文件为 Json 失败.")


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
                self.ssh.connect(hostname=self.ip, port=self.port,
                                 username=self.username, password=self.passwd, allow_agent=False)
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
        stdin, stdout, stderr = self.ssh.exec_command(cmd, get_pty=True, bufsize=1)
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


def init_env(ip, port, username, passwd, soft_list, deploy_method):
    # ip = '10.0.1.132'
    # port = 22
    # username = 'root'
    # passwd = '475869@hjl.cn'

    LOG.info('{}--{}--{}--{}--{}'.format(ip, port, username, passwd, soft_list))

    soft_str = ' '.join(soft_list)
    print(soft_str)
    client = RemoteLoginApi(ip, port, username, passwd)
    client.connect()

    print('connect {} sucess!!!'.format(ip))

    if deploy_method == 'python':

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
        local_path = os.path.join(os.getcwd(), 'scripts', 'install_soft.py')
        client.upload_file(local_path, '/root/install_soft.py')

        code, out, err = client.exec_cmd('python3 /root/install_soft.py {}'.format(soft_str))
        if code == 0:
            LOG.info('python3 /root/install_soft.py {}'.format(soft_str))
            LOG.debug(out)
        else:
            LOG.info(code)
            LOG.info(out)
            LOG.info(err)
    elif deploy_method == 'shell':
        local_path = os.path.join(os.getcwd(), 'scripts', 'install_soft.sh')
        client.upload_file(local_path, '/root/install_soft.sh')
        for soft in soft_list:
            if soft == 'zabbix_client':
                LOG.info('upload zabbix client to {}'.format(ip))
                local_path = os.path.join(os.getcwd(), 'package', 'zabbix-agent-x86_64.rpm')
                if not os.path.exists(local_path):
                    local_path = os.path.join(SOFT_PATH, 'linux', 'zabbix-agent-x86_64.rpm')
                print(local_path)
                client.upload_file(local_path, '/root/zabbix-agent.rpm')

                conf = read_yaml_to_json()
                zabbix_server_ip = conf.get('zabbix_client').get('zabbix_server_ip')

                name_prefix = conf.get('zabbix_client').get('zabbix_client_name')

                zabbix_client_name = name_prefix + '-' + ip

                param_str = soft + ' ' + zabbix_server_ip + ' ' + zabbix_client_name
                LOG.info('bash /root/install_soft.sh {}'.format(param_str))
                code, out, err = client.exec_cmd('bash /root/install_soft.sh {}'.format(param_str))
                print(code)
                LOG.info('add host to zabbix server .....server={},client={},{}'.format(zabbix_server_ip,
                                                                                        zabbix_client_name,
                                                                                        ip))
                add_host_to_zabbix_server(zabbix_server_ip, zabbix_client_name, ip)

    log_local_path = os.path.join(os.getcwd(), 'install.log')
    client.download_file('/root/install.log', log_local_path)


def install_soft(conf):
    '''
    安装资产软件服务如 telnet mysql ...
    :param conf:
    :return:
    '''
    host_list = conf.get('linux').get('hosts')
    for host in host_list:
        ip = host.get('ip')
        port = host.get('port')
        user = host.get('user')
        passwd = host.get('passwd')
        soft_list = host.get('softname')
        print(ip, port, user, passwd, soft_list)
        init_env(ip, port, user, passwd, soft_list, deploy_method)


def deploy_zabbix_client(conf):
    '''
    部署zabbix 客户端
    :param conf:
    :return:
    '''
    param = conf.get('zabbix_client')
    ip_list = param.get('zabbix_client_ip')
    port = param.get('zabbix_client_port')
    account = param.get('account')
    passwd = param.get('passwd')
    behavior = param.get('behavior')

    if behavior == 'add':
        # zabbix_server_ip = param.get('zabbix_server_ip')
        # zabbix_client_name = param.get('zabbix_client_name')
        soft_list = ['zabbix_client']

        LOG.info('start deploy_zabbix_client........')

        LOG.info('{}--{}--{}--{}--{}'.format(ip_list, port, account, passwd, soft_list))

        for ip in ip_list:
            threading.Thread(target=init_env, args=(ip, port, account, passwd, soft_list, 'shell')).start()
            # 修复 读取配置文件 报错 __file__ 未定义问题
            time.sleep(1)
    elif behavior == 'del':
        LOG.info('clear zabbix client from zabbix server ')
        # 清除服务端监控信息
        zabbix_server_ip = param.get('zabbix_server_ip')
        name_prefix = param.get('zabbix_client_name')
        for ip in ip_list:
            zabbix_client_name = name_prefix + '-' + ip
            LOG.info('clear client {} info from zabbix server {}..'.format(zabbix_client_name,zabbix_server_ip))
            threading.Thread(target=del_host_from_zabbix_server, args=(zabbix_server_ip, zabbix_client_name,)).start()
            time.sleep(1)
        # 清除监控主机相关安装客户端
        for ip in ip_list:
            LOG.info('clear client {} software.... '.format(ip))
            client = RemoteLoginApi(ip, port, account, passwd)
            client.connect()
            code, out, err = client.exec_cmd('rpm -qa | grep zabbix-agent  |xargs rpm -e ')
            print(code)


def deploy_soft(ip, port, username, passwd, script_name, param_list=None, dep_pack_list=None):
    '''
    :param ip:
    :param port:
    :param username:
    :param passwd:
    :param script_name:
    :param param_list:
    :param dep_pack_list:  执行脚本的依赖包
    :return:
    '''

    client = RemoteLoginApi(ip, port, username, passwd)
    client.connect()
    print('connect {} sucess!!!'.format(ip))

    if dep_pack_list:
        for pack in dep_pack_list:
            local_path = os.path.join(os.getcwd(), 'package', pack)
            if not os.path.exists(local_path):
                local_path = os.path.join(SOFT_PATH, 'linux', pack)
            remote_path = '/tmp/' + pack
            client.upload_file(local_path, remote_path)
    param_str = ''
    if param_list:
        param_str = ' '.join(param_list)
        print(param_str)

    local_path = os.path.join(os.getcwd(), 'scripts', script_name)
    remote_path = '/tmp/' + script_name
    client.upload_file(local_path, remote_path)

    LOG.info('bash {} {}'.format(remote_path, param_str))
    code, out, err = client.exec_cmd('bash {} {}'.format(remote_path, param_str))
    print(out)
    print(err)
    print(code)
    #
    log_local_path = os.path.join(os.getcwd(), 'install.log')
    client.download_file('/tmp/install.log', log_local_path)


def deploy_performance_host_env(conf):
    '''
    部署性能主机环境
    :param conf:
    :return:
    '''
    param = conf.get('performance_host_env')
    account = param.get('account')
    passwd = param.get('passwd')
    port = param.get('port')
    ip_list = param.get('host_list')
    script_name = 'performance_env_init.sh'
    dep_pack_list = ['rdpexec.tar.gz', 'performance_pip_lib.tar.gz']
    for ip in ip_list:
        deploy_soft(ip, port, account, passwd, script_name, dep_pack_list=dep_pack_list)


deploy_flag_dict = {
    '1': install_soft,
    '2': deploy_zabbix_client,
    '3': deploy_performance_host_env
}

if __name__ == '__main__':
    init_log()
    conf = read_yaml_to_json()
    deploy_method = conf.get('common').get('method')
    deploy_flag = conf.get('common').get('deploy_flag')
    SOFT_PATH = conf.get('common').get('soft_path')

    install_obj = deploy_flag_dict.get(str(deploy_flag))
    if not install_obj:
        print('不支持的部署方式......')
        exit(-1)
    install_obj(conf)
