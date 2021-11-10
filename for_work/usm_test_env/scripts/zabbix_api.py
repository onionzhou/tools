#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zhouey
@file: zabbix_api.py
@time: 2021/9/8 11:47
"""
import requests
import json


# zabbix api 文档
# https://www.zabbix.com/documentation/current/manual/api

class Zabbix():

    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def _post_data(self, payload):
        data = json.dumps(payload)
        ret = requests.post(self.url, data=data, headers=self.headers)
        # print(ret.text)
        return ret.json()

    def _get_login_token(self, name, passwd):
        payload = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": name,
                "password": passwd
            },
            "id": 1,
            "auth": None
        }

        ret = self._post_data(payload)
        # 40ba2ff0d36acf235059fb7aa401da88
        return ret.get('result')

    def get_group_id(self, authtoken, namelist: list):
        '''
        常用的两个组名为
        "Templates/Modules","Linux servers",
        :param authtoken:
        :param namelist:
        :return: dict ,key为查询名称name value 为groupid

        '''

        payload = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": "extend",
                "filter": {
                    "name": namelist
                }
            },
            "auth": authtoken,
            "id": 1
        }

        ret = self._post_data(payload)

        tmp_dict = {}
        for name in namelist:
            for data in ret.get('result'):
                if data.get('name') == name:
                    tmp_dict[name] = data.get('groupid')

        print(tmp_dict)
        return tmp_dict

    def get_template_id(self, authtoken, namelist: list):
        '''
        ["Linux by Zabbix agent"]
        :param authtoken:
        :param namelist:
        :return: dict key为查询名称name value为templeid
        '''

        payload = {
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": "extend",
                "filter": namelist
            },
            "auth": authtoken,
            "id": 1
        }
        ret = self._post_data(payload)
        tmp_dict = {}
        for name in namelist:
            for data in ret.get('result'):
                if data.get('name') == name:
                    tmp_dict[name] = data.get('templateid')

        print(tmp_dict)
        return tmp_dict

    def add_monitoring_host(self,
                            authtoken,
                            hostname,
                            ip,
                            groupid_dict: dict,
                            templateid_dict: dict):

        '''
        添加监控主机到zabbix 服务器中
        :param authtoken:
        :param ip:
        :param groupid_dict:
        :param templateid_dict:
        :return:  主机id列表   10449
        '''
        groupid_list = []
        for _, v in groupid_dict.items():
            groupid_list.append({'groupid': v})
        templateid_list = []
        for v in templateid_dict.values():
            templateid_list.append({'templateid': v})

        payload = {
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": hostname,
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": ip,
                        "dns": "",
                        "port": "10050"
                    }
                ],
                "groups": groupid_list,

                "templates": templateid_list,

            },
            "auth": authtoken,
            "id": 1
        }

        ret = self._post_data(payload)
        hostid_list = ret.get('result').get('hostids')
        return hostid_list

    def get_host_graph(self, authtoken, hostid: int):
        '''
        获取主机图形id
        :param authtoken:
        :param hostid:
        :return: dict   k 图形监控值得字符串，V 字符串所对应的id
        '''
        payload = {
            "jsonrpc": "2.0",
            "method": "graph.get",
            "params": {
                "output": "extend",
                "hostids": hostid,
                "sortfield": "name"
            },
            "auth": authtoken,
            "id": 1
        }

        ret = self._post_data(payload)
        alist = ret.get('result')
        tmp_dict = {}
        for d in alist:
            k = d.get('name')
            v = d.get('graphid')
            tmp_dict[k] = v

        print(tmp_dict)
        return tmp_dict

    def add_dashboard(self, authtoken, name, graph_dict):
        '''

        :param authtoken:
        :param name:   dashboard名
        :param graph_dict:
        :return:  list  dashboardids列表
        '''

        x_offset = 12
        y_offset = 5
        x_count = 0
        y_count = 0
        widgets_list = []
        for k, v in graph_dict.items():
            tmp_dict = {
                "type": "graph",
                "x": 0 + x_offset * (x_count % 2),
                "y": 0 + y_offset * y_count,
                "width": 12,
                "height": 5,
                "view_mode": 0,
                "fields": [
                    {
                        "type": "6",
                        "name": "graphid",
                        "value": v
                    },
                    {
                        "type": "0",
                        "name": "rf_rate",
                        "value": "10"  # 10s 获取一次值，默认1min
                    }

                ]
            }

            widgets_list.append(tmp_dict)
            x_count += 1

            if x_count % 2 == 0:
                y_count += 1

        payload = {
            "jsonrpc": "2.0",
            "method": "dashboard.create",
            "params": {
                "name": name,
                "display_period": 30,
                "auto_start": 1,
                "pages": [
                    {
                        "widgets": widgets_list
                    }
                ],

            },
            "auth": authtoken,
            "id": 1
        }

        ret = self._post_data(payload)

        return ret.get('result').get('dashboardids')

    def get_dashboard(self, authtoken):
        '''
        :param authtoken:  认证token
        :return:  字典  k=dashboard名，v=dashboard id
        {'Global view': '1', 'Zabbix server health': '2'}
        '''
        payload = {
            "jsonrpc": "2.0",
            "method": "dashboard.get",
            "params": {
                "output": "extend",
                "selectPages": "extend",
                "selectUsers": "extend",
                "selectUserGroups": "extend",

            },
            "auth": authtoken,
            "id": 1
        }

        ret = self._post_data(payload)
        # print(ret)
        tmp_dict = {}
        for i in ret.get('result'):
            k = i.get('name')
            v = i.get('dashboardid')
            tmp_dict[k] = v
        return tmp_dict

    def del_dashboard(self, autoken: str, ids_list: list) -> dict:
        '''

        :param autoken:
        :param ids_list:
        :return:
        '''

        payload = {
            "jsonrpc": "2.0",
            "method": "dashboard.delete",
            "params": ids_list,
            "auth": autoken,
            "id": 1
        }

        print(payload)
        ret = self._post_data(payload)
        return ret.get('result')

    def del_dashboard_by_name(self, authtoken: str, name: str):
        '''
        通过dashboard name 删除 dashboard
        :param authtoken:
        :param name:
        :return:
        '''
        ret = self.get_dashboard(authtoken)
        dashboardid = ret.get(name)
        if dashboardid is None:
            raise Exception('zabbix server is not exist < {} > dashboard'.format(name))

        ids_list = []
        ids_list.append(dashboardid)
        return self.del_dashboard(authtoken, ids_list)

    def get_host_id(self, authtoken: str, host_list: str):
        '''
        :param authtoken:
        :param host_list:
        :return: dict , key为主机名，value为主机id
        '''
        # host_list = ['usm_112']
        payload = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "filter": {
                    "host": host_list
                }
            },
            "auth": authtoken,
            "id": 1
        }

        ret = self._post_data(payload)

        tmp_dict = {}
        for i in ret.get('result'):
            k = i.get('host')
            v = i.get('hostid')
            tmp_dict[k] = v

        return tmp_dict

    def del_host(self, authtoken: str, hostids_list: list):
        payload = {
            "jsonrpc": "2.0",
            "method": "host.delete",
            "params": hostids_list,
            "auth": authtoken,
            "id": 1
        }
        ret = self._post_data(payload)
        print(ret)
        return ret.get('result')

    def del_host_by_name(self, authtoken: str, host_name: str):
        host_name_list = []
        host_id_list = []
        host_name_list.append(host_name)

        ret = self.get_host_id(authtoken, host_name_list)
        for v in ret.values():
            host_id_list.append(v)

        return self.del_host(authtoken, host_id_list)

    def get_audit_log(self, authtoken):

        payload = {
            "jsonrpc": "2.0",
            "method": "auditlog.get",
            "params": {
                "output": "extend",
                "sortfield": "clock",
                "sortorder": "DESC",
                "limit": 2
            },
            "auth": authtoken,
            "id": 1
        }
        ret = self._post_data(payload)
        print(ret)
        return ret

    def get_login_token(self, name, passwd):
        import os
        filename = 'auto.conf'
        file_path = os.path.join(os.getcwd(), filename)

        if not os.path.exists(file_path):
            print(1)
            admintoken = self._get_login_token(name, passwd)
            with open(filename, mode='w') as f:
                f.write(admintoken)
            return admintoken

        with open(filename, mode='r') as f:
            admintoken = f.readline()

        ret = self.get_audit_log(admintoken)
        if 'error' in ret:
            print('token invaid...,re-apply')
            os.remove(file_path)
            self.get_login_token(name,passwd)
        else:
            return admintoken

def add_host_to_zabbix_server(serverip: str, hostname: str, hostip: str):
    '''

    :param serverip: 10.0.6.219
    :param hostname:
    :param hostip:
    :return:
    '''
    headers = {
        "Content-Type": "application/json"
    }

    url = 'http://{}/zabbix/api_jsonrpc.php'.format(serverip)

    z = Zabbix(url, headers)

    authtoken = z.get_login_token('Admin', 'zabbix')
    # authtoken = '3e808686c7fd98c36e2b61e60fc6cdec'
    namelist = ['Templates/Modules', 'Linux servers']
    g_dict = z.get_group_id(authtoken, namelist)

    tem_namelist = ['Linux CPU by Zabbix agent',
                    'Linux filesystems by Zabbix agent',
                    'Linux generic by Zabbix agent',
                    'Linux memory by Zabbix agent',
                    'Linux network interfaces by Zabbix agent'
                    ]
    t_dict = z.get_template_id(authtoken, tem_namelist)
    host_id_list = z.add_monitoring_host(authtoken, hostname, hostip, g_dict, t_dict)

    data_dict = z.get_host_graph(authtoken, int(host_id_list[0]))

    z.add_dashboard(authtoken, hostname, data_dict)


def del_host_from_zabbix_server(serverip, hostname):
    headers = {
        "Content-Type": "application/json"
    }

    url = 'http://{}/zabbix/api_jsonrpc.php'.format(serverip)

    z = Zabbix(url, headers)
    authtoken = z.get_login_token('Admin', 'zabbix')
    # authtoken = '3e808686c7fd98c36e2b61e60fc6cdec'
    z.del_dashboard_by_name(authtoken, hostname)
    ret = z.del_host_by_name(authtoken, hostname)
    print(ret)


if __name__ == '__main__':
    add_host_to_zabbix_server('10.0.6.219', 'usm_112', '10.0.6.214')
    del_host_from_zabbix_server('10.0.6.219', 'usm_112')
