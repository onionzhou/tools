#!/bin/bash 
#将安装包与脚本放在同一个目录 
#软件安装好路径 /usr/local/app/nginx
#检查nginx 安装依赖 
#主函数main中更改具体软件包名称(soft_name)
function check_dependence(){
	var=$(rpm -qa | grep  pcre-devel |wc -l)
	if [ $var == 0 ];then
		yum install pcre-devel -y  
	fi
	
	var=$(rpm -qa | grep  pcre |wc -l)	
	
	if [ $var == 1 ];then
		yum install pcre -y 
	fi
	var=$(rpm -qa | grep  openssl-devel |wc -l)
	if [ $var == 0 ];then
		yum install openssl openssl-devel -y
	fi
	
	echo "check done"
}

function modify_config(){
	install_path='/usr/local/app/nginx'
	cd $install_path/conf
	cp nginx.conf nginx.conf.bak 
	#去除#号和空行
	egrep -v "#|^$" nginx.conf.bak  >nginx.conf
	nginx -t 
	[ $? -eq 0 ] && echo '>>>> modify nginx config sucessfull !!'\
	|| echo ">>> modify nginx config failed "
}

function install_nginx(){
	soft=$1
	basedir='nginx'
	install_path='/usr/local/app/nginx'
	[ ! -f $soft ] &&{
        echo " $soft Installation package not exist"
        exit 1
    }
	
	if [ ! -d $basedir ] ;then
		echo "create dir $basedir"
		mkdir $basedir 
	fi 
	
	useradd  nginx -s /sbin/nologin -M
	
	tar -zxvf $soft -C ./$basedir  --strip-components 1
	
	cd  $basedir
	
	./configure --user=nginx --group=nginx --prefix=$install_path \
	--with-http_stub_status_module --with-http_ssl_module
	
	make&&make install
	
	cd  $install_path/sbin
	
	./nginx -t 
	if [ $? == 0 ];then
		echo " cp nginx  to /usr/local/sbin "
		cp $install_path/sbin/nginx /usr/local/sbin 	
	else 
		echo "install failed！！"
	fi
	
}

function main(){
	soft_name='nginx-1.15.10.tar.gz'
	install_nginx $soft_name 
	modify_config
}

main
