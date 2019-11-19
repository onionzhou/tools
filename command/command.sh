#!/bin/bash 

# linux 常用命令集合

function command(){
	
	# 批量kill httpd 进程
	ps -ef | grep httpd | grep -v grep | cut -c 9-15 |xarges kill -9
	
	#查看常用端口
	netstat -nlpt
	
	#nginx 命令
	nginx -t  #检查配置文件正确性
	nginx -s reload #重载配置文件
	nginx -s quit  #待nginx进程处理任务完毕后停止
	nginx -s stop #停止
	nginx   #启动 
}

function centos_command(){
	#查看防火墙状态
	firewall-cmd --state

	#停止firewall
	systemctl stop firewalld.service

	#禁止firewall开机启动
	systemctl disable firewalld.service

}