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
	
	#rpm 相关指令
	rpm -qa | grep php
	rpm -e   #卸载
	rpm -i   #安装
	#yum  相关指令 
	yum install 
	yum update 
	yum remove  
	yum search 
	yum list | grep php
	yum clean all
	yum makecache 
	
	#vim 相关操作 
	# :3,5 copy 6  #多行复制
	
}
function gunicorn(){
	#启动命令
	/usr/local/bin/python3.6 /usr/local/bin/gunicorn -w 2 \
	--log-level info --access-logfile /usr/local/app/gun_log/access.log --error-logfile \
	/usr/local/app/gun_log/error.log -b 127.0.0.1:8000 blog:app -D
	
	#gunicorn --log-level info --access-logfile /var/log/httpbin/access.log --error-logfile /var/log/httpbin/error.log -b 0.0.0.0:8001 httpbin:app 
}

function centos_command(){
	#查看防火墙状态
	firewall-cmd --state

	#停止firewall
	systemctl stop firewalld.service

	#禁止firewall开机启动
	systemctl disable firewalld.service

}

function git_command(){
	#git 代理设置
	git config --global https.proxy 'http://127.0.0.1:1080'

	git config --global https.proxy 'https://127.0.0.1:1080'

	git config --global http.proxy  'socks5://127.0.0.1:10808' 

	git config --global https.proxy 'socks5://127.0.0.1:10808'
	#git 取消代理
	git config --global --unset http.proxy

	git config --global --unset https.proxy
	
	#git 修改commit 注释
	git commit --amend
	
	#git 统计代码行数
	#added lines: xxx, removed lines: xx, total lines: xxx
	git log --author="onionzhou" \
	--pretty=tformat: --numstat | \
	awk '{ add += $1; subs += $2; loc += $1 - $2 } END { printf "added lines: %s, removed lines: %s, total lines: %s\n", add, subs, loc }' -

}
#git 批量修改已经提交历史的代码的的用户和邮箱
function git_modify_user_email(){

	1. git clone --bare https://github.com/onionzhou/tools.git <你需要修改的工程>
	2. cd tools.git
	3. 
	#!/bin/sh
	git filter-branch --env-filter '

	OLD_EMAIL="旧的email地址"
	CORRECT_NAME="正确的用户"
	CORRECT_EMAIL="新的email地址"

	if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]
	then
		export GIT_COMMITTER_NAME="$CORRECT_NAME"
		export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
	fi
	if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]
	then
		export GIT_AUTHOR_NAME="$CORRECT_NAME"
		export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
	fi
	' --tag-name-filter cat -- --branches --tags

	4.  git push --force --tags origin 'refs/heads/*'   # push to  github
	#删除刚clone 的工程
	5. cd .. ; rm -rf tools.git
	
}




