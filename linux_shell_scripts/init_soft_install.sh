#!/bin/bash
PYTHON_PACKAGE='Python-3.6.5.tgz'

#python 包安装 ，将python安装包和脚本放在同一目录
#路径 /usr/local
function install_python(){
    soft=$1
	basedir='Python'

    [ ! -f $soft ] &&{
        echo " $soft Installation package not exist"
        exit 1
    }
	
	if [ ! -d $basedir ] ;then
		echo "create dir $basedir"
		mkdir $basedir 
	fi 
	
	tar -zxvf $soft -C ./$basedir  --strip-components 1
	
	cd  $basedir
	
	./configure --prefix=/usr/local
	
	make&&make install
	
	if [ 0 -eq $? ];then
		echo "install python successfull! " >>install.log 
	else
		echo " install python failed!!" >> install.log
		exit -1
	fi
}

#修改pip 源
function modify_pip_source(){

	[ ! -d ~/.pip ] && {
		echo "create ~/.pip " >> install.log
		mkdir -p ~/.pip
	} 
	
	if [ ! -f ~/.pip/pip.conf ]
	then
		echo "create ~/.pip/pip.conf "	>>install.log
		touch  ~/.pip/pip.conf
	else
		mv ~/.pip/pip.conf ~/.pip/pip.conf.bak 
		touch  ~/.pip/pip.conf
	fi 
	echo "write conf to pip.conf" >> install.log
	echo  >> ~/.pip/pip.conf
	echo "[global]" >> ~/.pip/pip.conf
	echo "index-url = https://pypi.tuna.tsinghua.edu.cn/simple" >> ~/.pip/pip.conf

}

function install_pip(){

	wget --no-check-certific ate https://pypi.python.org/packages/source/p/pip/pip-10.0.1.tar.gz >>/dev/null
	tar -zvxf pip-10.0.1.tar.gz >> /dev/null
	cd pip.10.0.1
	python3 setup.py build
	python3 setup.py install
	
	if [ 0 -eq $? ];then
		echo "install pip successfull! " >>install.log 
	else
		echo " install pip failed!!" >> install.log
		exit -1
	fi

}

function install_ipython(){
	cmd=$(which pip3)
	echo "$cmd" |grep "no pip3"
	if [ 0 -eq $? ];then
		echo "install pip3" >> install.log	
		#install_pip
	fi 
	
	$cmd install ipython 
	
	if [ 0 -eq $? ] ;then 
		echo "install ipython success" >> install.log
	else
		echo 'install ipython failed ' >> install.log
		exit 1
	fi
}
#安装python相关依赖
function init_install_python(){
	install_python $PYTHON_PACKAGE
	modify_pip_source
	install_ipython
}

function check_dependence(){
	yum install zlib* -y

	var=$(rpm -qa | grep  openssl-devel |wc -l)
	if [ $var == 0 ];then
		yum install openssl openssl-devel -y
	fi

	echo "check done"
}

#########################################################

function main(){
    check_dependence
    init_install_python
}

#主函数入口
main