#!/bin/bash

PARAM=$*

LOG_FILE=install.log

function init_log(){
    cat /dev/null > $LOG_FILE
}

function install_zabbix_client(){
    zabbix_server_ip=$1
    zabbix_client_name=$2

    echo "$zabbix_server_ip    $zabbix_client_name"

    echo "install zabbix client...." >>$LOG_FILE
    echo "rpm -ivh zabbix-agent.rpm " >> $LOG_FILE
    rpm -ivh zabbix-agent.rpm  >> $LOG_FILE

    echo "modify zabbix.conf " >>$LOG_FILE

    if [ -f '/etc/zabbix/zabbix_agentd.conf' ] ; then
        mv -f  /etc/zabbix/zabbix_agentd.conf  /etc/zabbix/zabbix_agentd.conf.bak

    fi

    cat /dev/null > /etc/zabbix/zabbix_agentd.conf
    echo "PidFile=/var/run/zabbix/zabbix_agentd.pid" >>/etc/zabbix/zabbix_agentd.conf
    echo "LogFile=/var/log/zabbix/zabbix_agentd.log" >>/etc/zabbix/zabbix_agentd.conf
    echo "LogFileSize=0" >>/etc/zabbix/zabbix_agentd.conf
    echo "Include=/etc/zabbix/zabbix_agentd.d/*.conf" >>/etc/zabbix/zabbix_agentd.conf
    echo "Server=$zabbix_server_ip" >>/etc/zabbix/zabbix_agentd.conf
    echo "ServerActive=$zabbix_server_ip" >>/etc/zabbix/zabbix_agentd.conf
    echo "Hostname=$zabbix_client_name" >>/etc/zabbix/zabbix_agentd.conf

    echo "start zabbix client....." >> $LOG_FILE
    systemctl start zabbix-agent >> $LOG_FILE

    if [ $?  -ne 0 ];then
        echo "start zabbix client failed...." >>$LOG_FILE
    else
        echo "start zabbix client sucess...." >>$LOG_FILE
    fi

    sleep 1

    systemctl status  zabbix-agent >> $LOG_FILE

}

function main(){

    init_log
    echo " param: $@ "
    echo $1 >>$LOG_FILE

    if [ "$1" == 'zabbix_client' ];then
        # $1=softname  $2=zabbix server ip   $3=zabbixclient name
        echo 'install zabbix_client...' >>$LOG_FILE
        install_zabbix_client $2 $3
    else
        echo "not support install $1" >>$LOG_FILE
    fi

}

main $@
