### 注意

本脚本暂未做过多的出错处理，请确保你的目标机网络是畅通的，

软件顺序安装，如果第一个安装出错，会直接终止安装程序

在使用shell 脚本部署时候，请手动将脚本文档格式转换为unix(LF) 文档格式

### 执行

- python3 main.py



### 配置文件 

config.yaml

```
common:
 method: shell #  部署方式 python 或 shell
 deploy_host_os: linux   #部署主机系统可选(linux windows all),

linux:
 hosts:
 - ip: 10.0.1.132
   port: 22
   user: root
   passwd: '123456' #475869@hjl.cn
   softname:
   - mysql_v8.0.24
   - mysql_v5.7
   - telnet
   - db2_v10.5
   - zabbix_client  # 部署方式shell脚本
windows:

zabbix_client:  # 相关配置文件
    zabbix_server_ip: 10.0.1.220
    zabbix_client_name: usm200_31.131
```

### 支持安装的软件

- linux
  - mysql  v8.0  docker版
  - telnet
  - mysql v 5.7  docker版本
  - db2_10.5  （docker） 

### 软件名

```
linux :
	mysql_v8.0.24
	telnet
	mysql_v5.7
	db2_v10.5
	zabbix_client
```

### 软件端口

| 协议          | 端口  |
| ------------- | ----- |
| mysql_v8.0.24 | 3306  |
| telnet        | 23    |
| mysql_v5.7    | 3307  |
| db2_v10.5     | 50000 |



### 软件安装注意事项

- 安装环境 centos7.5

- 不支持离线安装，确保网络能够连接

- mysql_v8.0.24 
  - 账号/密码    root/123456
  
- mysql_v5.7
  - 账号/密码   root/123456
  
- db2_v10.5 

  - 账号/密码  db2inst1/db2inst1   dbname：mydb  

    

### 安装日志

- exec.log     main.py 调试日志
- install.log   远端主机上安装软件所产生的日志

