#!/bin/bash 

#关闭selinux 功能，需要重启系统
function shutdown_selinux(){
	sed -i s/SELINUX=enforcing/SELINUX=disabled/g /etc/selinux/config
	setenforce 0	
}

function ssh_config(){
	cp /etc/ssh/sshd_config /etc/ssh/sshd_config.$(date +%F%H%M%S)
	#修改ssh 默认端口
	#sed -i 's%#Port 22%Port 22222%' /etc/ssh/sshd_config
	sed -i 's%#UseDNS yes%#UseDNS no%' /etc/ssh/sshd_config
	sed -i 's%#PermitRootLogin yes%#PermitRootLogin no%' /etc/ssh/sshd_config
	CMD=$(which sshd)
	$CMD reload
}

#内核调优
function kernel_tuning(){
	
	#如果套接字由本端要求关闭，这个参数决定了它保持在FIN-WAIT-2状态的时间。
	#对端可以出错并永远不关闭连接，甚至意外当机。缺省值是60 秒。
	#2.2 内核的通常值是180秒，你可以按这个设置，但要记住的是，即使你的机器是一个轻载的WEB服务器，
	#也有因为大量的死套接字而内存溢出的风险，FIN- WAIT-2的危险性比FIN-WAIT-1要小，
	#因为它最多只能吃掉1.5K内存，但是它们的生存期长些。
	echo "net.ipv4.tcp_fin_timeout = 2" >>/etc/sysctl.conf
	echo "net.ipv4.tcp_keepalive_time = 500" >>/etc/sysctl.conf
	#开启TCP连接复用功能，允许将time_wait sockets重新用于新的TCP连接（主要针对time_wait连接）
	echo "net.ipv4.tcp_tw_reuse = 1"  >>/etc/sysctl.conf 
	#开启TCP连接中time_wait sockets的快速回收
	echo "net.ipv4.tcp_tw_recycle = 1"  >>/etc/sysctl.conf 	
	#对外连接端口范围
	echo "net.ipv4.ip_local_port_range = 4000 65000"  >>/etc/sysctl.conf
	#记录的那些尚未收到客户端确认信息的连接请求的最大值。
	#对于有128M内存的系统而言，缺省值是1024，小内存的系统则是128
	echo "net.ipv4.tcp_max_syn_backlog = 16384"  >>/etc/sysctl.conf 
	#timewait的数量，默认是180000
	echo "net.ipv4.tcp_max_tw_buckets = 36000" >>/etc/sysctl.conf	
	#在内核放弃建立连接之前发送SYN包的数量
	echo "net.ipv4.tcp_syn_retries = 1" >>/etc/sysctl.conf  	
	#为了打开对端的连接，内核需要发送一个SYN并附带一个回应前面一个SYN的ACK。
	#也就是所谓三次握手中的第二次握手。这个设置决定了内核放弃连接之前发送SYN+ACK包的数量
	echo "net.ipv4.tcp_synack_retries = 1"  >>/etc/sysctl.conf 
	
	#每个网络接口接收数据包的速率比内核处理这些包的速率快时，允许送到队列的数据包的最大数目
	echo "net.core.netdev_max_backlog = 16384"  >>/etc/sysctl.conf
	
	#web应用中listen函数的backlog默认会给我们内核参数的net.core.somaxconn限制到128，
	#而nginx定义的NGX_LISTEN_BACKLOG默认为511，所以有必要调整这个值
	echo "net.core.somaxconn = 16384"  >>/etc/sysctl.conf
	
	#系统中最多有多少个TCP套接字不被关联到任何一个用户文件句柄上。
	#这个限制仅仅是为了防止简单的DoS攻击，不能过分依靠它或者人为地减小这个值，更应该增加这个值(如果增加了内存之后)
	echo "net.ipv4.tcp_max_orphans = 3276800"  >>/etc/sysctl.conf
	
	# 避免放大攻击
	#net.ipv4.icmp_echo_ignore_broadcasts = 1

	# 开启恶意icmp错误消息保护
	#net.ipv4.icmp_ignore_bogus_error_responses = 1
		
	sysctl -p /etc/sysctl.conf
		
}	 



function sys_config(){
	#文件句柄设置
	echo "* - nofile 65535" >> /etc/security/limits.conf	
	kernel_tuning
	
}

function modify_centos7_yumsource(){

	wget http://mirrors.aliyun.com/repo/Centos-7.repo
	mv  /etc/yum.repos.d/CentOS-Base.repo  /etc/yum.repos.d/CentOS-Base.repo.$(date +%F%H%M%S)
	cp  ./Centos-7.repo /etc/yum.repos.d/CentOS-Base.repo

	yum clean all # 清除系统所有的yum缓存
	yum makecache # 生成yum缓存

}

function cmd_install(){
	#lsb_release 
	yum install -y redhat-lsb
	#sar iostat  
	yum -y install sysstat
	#network Monitoring
	yum -y install iptraf
	#disk io test tools 
	yum install libaio-devel fio
	#host dependence
	yum -y install zlib*
	yum install pcre-devel -y
	yum install pcre -y
	yum install openssl openssl-devel -y
	
}

function main(){
	sys_config
	#ssh_config
	shutdown_selinux
	modify_centos7_yumsource
	cmd_install
}

#
main 



