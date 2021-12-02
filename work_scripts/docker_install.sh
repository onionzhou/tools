#!/bin/bash 


function install_docker()
{

    curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
    
}

function setting_docker()
{
    yum install -y yum-utils device-mapper-persistent-data lvm2
     
    #配置源 
    yum-config-manager --add-repo \
    https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/centos/docker-ce.repo
    #安装 Docker Engine-Community
    yum install docker-ce docker-ce-cli containerd.io
    
}


function cmd(){

    systemctl start docker
    
    docker run hello-world  # 验证是否正确安装了 Docker Engine-Community
    
    yum remove docker-ce  #删除安装包
    
    rm -rf /var/lib/docker #删除镜像、容器、配置文件等内容
    
    docker pull mysql:8.0.24  
    # docker qidong 
    docker run -itd --name mysql-test -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql 
    
    docker  rmi -f <image_id>
    
    #mysql
    GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION
    
    FLUSH PRIVILEGES;
    
    # 改变密码的加密规则
    ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'YourRootPassword';
    
    create user 'test'@'%' identified by '123456';
    
    grant all privileges on *.*  to  'test'@'%'  identified by '123456'  with grant option;
    
    https://hub.docker.com/_/mysql?tab=tags
    
    
    select host, user, authentication_string, plugin from user;
    
     
}


function main(){

    docker exec -it mysql_v8.0.24 bash
    sleep 1
    mysql -u root --password=123456
    sleep 1
    use mysql;
    
    docker exec -it mysql_v8.0.22 bash -c 'mysql -u root -h 127.0.0.1 --password=123456'
    
    

}


main