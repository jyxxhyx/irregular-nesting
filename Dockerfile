FROM centos:7.4.1708
 
MAINTAINER Tom Sun 414776205@qq.com
 
#下载安装包并且创建python的运行环境
RUN yum -y install wget \
&& yum install gcc -y \
&& yum install zlib* -y \
&& yum install openssl* -y \
&& yum install tar -y \
&& yum install libffi-devel -y \
&& yum install openssl-devel -y

RUN wget https://www.python.org/ftp/python/3.6.7/Python-3.6.7.tgz \
&&  tar -xzvf Python-3.6.7.tgz

 
#安装Python
RUN ./Python-3.6.7/configure --prefix=/usr/local --with-ssl\
&& make \
&& make install
 
#创建Python文件的存放目录
RUN mkdir -p /workspace/python_file
#COPY test /workspace/python_file
 
#安装Python的相关库
 
RUN pip3 install --upgrade pip \
&&pip3 install numpy==1.15.2 -i https://pypi.tuna.tsinghua.edu.cn/simple \
&&pip3 install matplotlib==3.1.1 -i https://pypi.tuna.tsinghua.edu.cn/simple \
&&pip3 install pyclipper==1.1.0.post1 -i https://pypi.tuna.tsinghua.edu.cn/simple \
&&pip3 install Shapely==1.6.4.post2 -i https://pypi.tuna.tsinghua.edu.cn/simple \
&&pip3 install typing==3.7.4.1 -i https://pypi.tuna.tsinghua.edu.cn/simple \
&&pip3 install ujson==1.35 -i https://pypi.tuna.tsinghua.edu.cn/simple\
&&pip3 install PyYAML==5.1.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
