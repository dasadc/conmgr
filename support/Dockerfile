FROM ubuntu:14.04 
RUN apt-get update && apt-get clean
MAINTAINER Seiya SHIBATA shibasay

ENV SDKURL https://storage.googleapis.com/appengine-sdks/featured/google_appengine_1.9.38.zip
ENV ROOTPASSWORD hogehoge

# Install ssh

RUN apt-get install -y openssh-server
RUN mkdir /var/run/sshd
RUN echo 'root:${ROOTPASSWORD}' | chpasswd
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

#RUN echo "root:${ROOTPASSWORD}" |chpasswd
#RUN sed -ri 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config
#RUN sed -ri 's/PermitRootLogin without-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
#RUN sed -ri 's/#PasswordAuthentication yes/PasswordAuthentication yes/g' /etc/ssh/sshd_config
#RUN sed -ri 's/#AuthorizedKeysFile/AuthorizedKeysFile/g' /etc/ssh/sshd_config

# Install Additional packages and dependancies

RUN apt-get install -y sudo wget curl zip zsh build-essential

# Install popular python packages

RUN apt-get install -y python2.7 python-pip
# python-dev is required for building numpy
RUN apt-get install -y python-dev
RUN pip install numpy==1.6.1

# Install Google AppEngine for python SDK

ADD $SDKURL /tmp/gae.zip
RUN cd /usr/local && unzip /tmp/gae.zip
RUN ln -s /usr/local/google_appengine/dev_appserver.py   /usr/local/bin
RUN ln -s /usr/local/google_appengine/appcfg.py          /usr/local/bin
RUN ln -s /usr/local/google_appengine/_python_runtime.py /usr/local/bin

EXPOSE 22
EXPOSE 8080
CMD ["/usr/sbin/sshd", "-D"]

