#!/bin/bash 
#将安装包与脚本放在同一个目录 
#软件安装好路径 /usr/local/app/mongodb


SOFT_DIR='/usr/local/app/mongodb'

function install_soft(){
	pack_name=$(ls |grep mongodb-*)
	echo $pack_name
	tar -zxvf $pack_name
	if [ ! -d $SOFT_DIR ]
	then
		mkdir -p $SOFT_DIR
	fi 
	#if  pack_name = xxx.tgz 
	#--->dir_name= xxx
	dir_name=${pack_name%*.*}
	echo "$dir_name"
	cp -a  $dir_name/*  $SOFT_DIR
	echo "install soft success!"

}

#用于修改配置文件涉及的目录或文件权限
function permiss_modify(){
	mkdir $SOFT_DIR/db
	mkdir $SOFT_DIR/log
	chmod 777 $SOFT_DIR/db
	chmod 777 $SOFT_DIR/log

}
#mongodb 配置文件写入
#args: conf_file 
function write_conf(){
	conf_file=$1
	echo "port=27017" >> $conf_file
	echo "dbpath=$SOFT_DIR/db" >> $conf_file
	echo "logpath=$SOFT_DIR/log/mongodb.log" >> $conf_file
	echo "logappend=true" >> $conf_file
	#以守护进程的方式运行，创建服务器进程
	echo "fork=true">> $conf_file
	#最大同时连接数
	echo "maxConns=100" >> $conf_file
	#不启用验证
	echo "noauth=true" >> $conf_file
	#每次写入会记录一条操作日志（通过journal可以重新构造出写入的数据）
	echo "journal=true" >> $conf_file
	#即使宕机，启动时wiredtiger会先将数据恢复到最近一次的
	#checkpoint点，然后重放后续的journal日志来恢复
	#存储引擎有mmapv1、wiretiger、mongorocks
	echo "storageEngine=wiredTiger" >> $conf_file
	echo "bind_ip = 0.0.0.0" >> $conf_file
	#开启认证
	#echo "auth=true" >> $conf_file
	
	permiss_modify
}


function gen_conf(){
	conf_file="$SOFT_DIR/mongodb.conf"
	if [ -f conf_file ];then
		echo "存在 $conf_file"
		mv $conf_file ${conf_file}.bak
		write_conf $conf_file
	else
		write_conf $conf_file
	fi 
	echo "gen conf suceess!!"

}

#mong 命令 
function command(){
	#如何远程连接mongo数据库
	#https://blog.csdn.net/onionnmmn/article/details/93364202
	#mongodb 基本操作
	#https://blog.csdn.net/onionnmmn/article/details/91318141
	#
	#
	#启动
	mongodb --config xxx.conf
	
	#使用admin数据库
	use admin
	
	#给admin数据库添加管理员用户名和密码，用户名和密码请自行设置
	db.createUser({user:"admin",pwd:"123456",roles:["root"]})

	#验证是否成功，返回1则代表成功
	db.auth("admin", "123456")

	#切换到要设置的数据库,以test为例
	use test

	#为test创建用户,用户名和密码请自行设置。
	db.createUser({user: "test", pwd: "123456", roles: [{ role: "dbOwner", db: "test" }]})
}

function main(){
	install_soft
	gen_conf
}

main