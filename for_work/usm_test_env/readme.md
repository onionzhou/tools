### 注意

本脚本暂未做过多的出错处理，请确保你的目标机网络是畅通的，

软件顺序安装，如果第一个安装出错，会直接终止安装程序

### 执行

- python3 main.py



### 配置文件 

config.yaml

```
linux:
 hosts:
 - ip: 10.0.1.132   #目标机
   port: 22         # 端口
   user: root       # 登陆账号
   passwd: '475869@hjl.cn'  #登陆密码
   softname:
   - mysql_v8.0.24  # 需要安装的软件名
   - telnet
   - mysql_v5.7
windows:

```

### 支持安装的软件

- linux
  - mysql  v8.0  docker版
  - telnet
  - mysql v 5.7  docker版本

### 软件名

```
linux :
	mysql_v8.0.24
	telnet
	mysql_v5.7
```

### 软件端口

| 协议          | 端口 |
| ------------- | ---- |
| mysql_v8.0.24 | 3306 |
| telnet        | 23   |
| mysql_v5.7    | 3307 |



### 软件安装注意事项

- 安装环境 centos7.5
- 不支持离线安装，确保网络能够连接

- mysql_v8.0.24 
  - 账号/密码    root/123456
- mysql_v5.7
  - 账号/密码   root/123456

### 安装日志

- exec.log     main.py 调试日志
- install.log   远端主机上安装软件所产生的日志

