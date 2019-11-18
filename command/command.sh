#!/bin/bash 

# linux 常用命令集合

function command(){
	
	# 批量kill httpd 进程
	ps -ef | grep httpd | grep -v grep | cut -c 9-15 |xarges kill -9
	
	#查看常用端口
	netstat -nlpt
}