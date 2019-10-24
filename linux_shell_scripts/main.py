#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/24 13:58
# @Author  : onion
# @Site    : 
# @File    : main.py
# @Software: PyCharm
import subprocess

def check_network():

    # tmp = subprocess.call(['ping','-c','4','www.baidu.com'])
    tmp = subprocess.call('ping -c 4 www.baidu.com',shell=True)
    if tmp != 0 :
        print('网络不可达，检查你的网络')
        exit(1)
    subprocess.call(['bash','init_config.sh'])


def main():
    check_network()

if __name__ == '__main__':
    main()

