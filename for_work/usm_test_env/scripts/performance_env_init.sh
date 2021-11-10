#!/bin/bash 

LOG_FILE=/tmp/install.log


function init_log(){
    cat /dev/null > $LOG_FILE
}


#关闭selinux 功能，需要重启系统
function shutdown_selinux(){

    echo "begin shutdown_selinux..."
    echo "begin shutdown_selinux..." >>$LOG_FILE

	sed -i s/SELINUX=enforcing/SELINUX=disabled/g /etc/selinux/config
	setenforce 0

    echo "end shutdown_selinux..."
    echo "end shutdown_selinux..." >>$LOG_FILE
}

function ssh_config(){
    echo "begin ssh_config..."
    echo "begin ssh_config..." >>$LOG_FILE

	cp /etc/ssh/sshd_config /etc/ssh/sshd_config.$(date +%F%H%M%S)
	#修改ssh 默认端口
	#sed -i 's%#Port 22%Port 22222%' /etc/ssh/sshd_config
	sed -i 's%#UseDNS yes%#UseDNS no%' /etc/ssh/sshd_config
	sed -i 's%#PermitRootLogin yes%#PermitRootLogin no%' /etc/ssh/sshd_config
	CMD=$(which sshd)
	$CMD reload

    echo "end ssh_config..."
    echo "end ssh_config..." >>$LOG_FILE
}

#内核调优
function kernel_tuning(){
	echo "begin kernel_tuning..."
	echo "begin kernel_tuning..." >>$LOG_FILE

	echo "net.ipv4.tcp_fin_timeout = 2" >>/etc/sysctl.conf
	echo "net.ipv4.tcp_keepalive_time = 500" >>/etc/sysctl.conf
	echo "net.ipv4.tcp_tw_reuse = 1"  >>/etc/sysctl.conf 
	echo "net.ipv4.tcp_tw_recycle = 1"  >>/etc/sysctl.conf 	
	echo "net.ipv4.ip_local_port_range = 4000 65000"  >>/etc/sysctl.conf
	echo "net.ipv4.tcp_max_syn_backlog = 16384"  >>/etc/sysctl.conf 
	echo "net.ipv4.tcp_max_tw_buckets = 36000" >>/etc/sysctl.conf	
	echo "net.ipv4.tcp_syn_retries = 1" >>/etc/sysctl.conf  	
	echo "net.ipv4.tcp_synack_retries = 1"  >>/etc/sysctl.conf 
	echo "net.core.netdev_max_backlog = 16384"  >>/etc/sysctl.conf
	echo "net.core.somaxconn = 16384"  >>/etc/sysctl.conf
	echo "net.ipv4.tcp_max_orphans = 3276800"  >>/etc/sysctl.conf
	
	#net.ipv4.icmp_echo_ignore_broadcasts = 1

	#net.ipv4.icmp_ignore_bogus_error_responses = 1
		
	sysctl -p /etc/sysctl.conf

	echo "end kernel_tuning..."
	echo "end kernel_tuning..." >>$LOG_FILE

}	 


function sys_config(){
	#文件句柄设置
	echo "begin sys_config..."
	echo "begin sys_config..." >>$LOG_FILE

	echo "* - nofile 65535" >> /etc/security/limits.conf
	kernel_tuning

	echo "end sys_config..."
	echo "end sys_config..." >>$LOG_FILE

}

function modify_centos7_yumsource(){

	echo "begin modify_centos7_yumsource..."
	echo "begin modify_centos7_yumsource..." >>$LOG_FILE

	#wget http://mirrors.aliyun.com/repo/Centos-7.repo
    curl -O http://mirrors.aliyun.com/repo/Centos-7.repo
	mv  /etc/yum.repos.d/CentOS-Base.repo  /etc/yum.repos.d/CentOS-Base.repo.$(date +%F%H%M%S)
	cp  ./Centos-7.repo /etc/yum.repos.d/CentOS-Base.repo
	yum clean all 
	yum makecache

    echo "end modify_centos7_yumsource..."
	echo "end modify_centos7_yumsource..." >>$LOG_FILE

}
#修改 pip 源
function modify_pip_source(){

    echo "begin modify_pip_source....."
    echo "begin modify_pip_source....." >>$LOG_FILE

	[ ! -d ~/.pip ] && {
		echo "create ~/.pip " >> $LOG_FILE
		mkdir -p ~/.pip
	} 
	
	if [ ! -f ~/.pip/pip.conf ]
	then
		echo "create ~/.pip/pip.conf "	>> $LOG_FILE
		touch  ~/.pip/pip.conf
	else
		mv ~/.pip/pip.conf ~/.pip/pip.conf.bak 
		touch  ~/.pip/pip.conf
	fi 
	echo "write conf to pip.conf" >> $LOG_FILE
	echo  >> ~/.pip/pip.conf
	echo "[global]" >> ~/.pip/pip.conf
	echo "index-url = https://pypi.tuna.tsinghua.edu.cn/simple" >> ~/.pip/pip.conf
    echo "[install]" >> ~/.pip/pip.conf
    echo "trusted-host=pypi.tuna.tsinghua.edu.cn" >> ~/.pip/pip.conf


    echo "end modify_pip_source....."
    echo "end modify_pip_source....." >>$LOG_FILE

}


function install_performance_dep(){
    echo "begin install_performance_dep"
    echo "begin install_performance_dep" >> $LOG_FILE

    cd /tmp
    pip_lib_name='performance_pip_lib'
    tar -zxvf ${pip_lib_name}.tar.gz && cd ${pip_lib_name} && pip3 install --no-index --find-links=./ -r requirements.txt
    cd ..
    rdp_lib_name='rdpexec'
    tar -zxvf ${rdp_lib_name}.tar.gz  -C /

    echo "end install_performance_dep"
    echo "end install_performance_dep" >> $LOG_FILE

}


function cmd_install(){

    echo "begin cmd_install"
    echo "begin cmd_install" >> $LOG_FILE
	#lsb_release
	echo "install redhat-lsb" >> $LOG_FILE
	yum install -y redhat-lsb
	#sar iostat
	echo "install sysstat" >> $LOG_FILE
	yum -y install sysstat
	#network Monitoring
	echo "install iptraf" >> $LOG_FILE
	yum -y install iptraf
	#disk io test tools
	echo "install libaio-devel fio" >> $LOG_FILE
	yum install libaio-devel fio  -y
	#host dependence
	echo "install zlib*" >> $LOG_FILE
	yum -y install zlib*

	echo "install pcre-devel pcre" >> $LOG_FILE
	yum install pcre-devel -y
	yum install pcre -y

	echo "install openssl-devel-devel openssl" >> $LOG_FILE
	yum install openssl openssl-devel -y
	echo "install python3 net-tools" >> $LOG_FILE
    yum install net-tools -y
    yum install python3 -y

    echo "end cmd_install"
    echo "end cmd_install" >> $LOG_FILE
	
}

function time_statistics(){
# 统计个函数的耗时情况

    func_name=$1

    startTime=$(date +%Y%m%d-%H:%M)
    startTime_s=$(date +%s)

    $func_name

    endTime=$(date +%Y%m%d-%H:%M)
    endTime_s=$(date +%s)
    sumTime=$[ $endTime_s - $startTime_s ]

    echo "$func_name $startTime ---> $endTime" "Totl:$sumTime s"
    echo "$func_name $startTime ---> $endTime" "Totl:$sumTime s" >>$LOG_FILE

}


function main(){
    time_statistics init_log
	time_statistics sys_config
	#ssh_config
	time_statistics shutdown_selinux
	time_statistics modify_centos7_yumsource
	time_statistics cmd_install
    time_statistics modify_pip_source
    time_statistics install_performance_dep
    echo "env config ok....." >> $LOG_FILE
}

#
main 


