#!/bin/bash
PYTHON_PACKAGE='Python-3.6.5.tgz'

#python 包安装 
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
	
	[ 0 -eq $? ] && echo "install python successfull! " \
				|| echo " install python failed!!"
}

#修改pip 源
function modify_pip_source(){

	[ ! -d ~/.pip ] && {
		echo "create ~/.pip "
		mkdir -p ~/.pip
	} 
	
	if [ ! -f ~/.pip/pip.conf ]
	then
		echo "create ~/.pip/pip.conf "	
		touch  ~/.pip/pip.conf
	else
		mv ~/.pip/pip.conf ~/.pip/pip.conf.bak 
		touch  ~/.pip/pip.conf
	fi 
	
	echo  >> ~/.pip/pip.conf
	echo "[global]" >> ~/.pip/pip.conf
	echo "index-url = https://pypi.tuna.tsinghua.edu.cn/simple" >> ~/.pip/pip.conf

}

function install_ipython(){
	cmd=$(which pip3)
	echo "$cmd"
	$cmd install ipython 
	
	if [ 0 -eq $? ] ;then 
		echo "install success ful "
	else
		echo 'install failed '
		exit 1
	fi
}
#安装python相关依赖
function init_install_python(){
	#install_python $PYTHON_PACKAGE
	#modify_pip_source
	install_ipython
}
#########################################################

function main(){
    init_install_python
}

#主函数入口
main