#!/bin/bash

set -x

apt-get update
apt-get install -y python3 python3-pip tmux git vim visidata unzip jq

curl -L https://github.com/dolthub/dolt/releases/latest/download/install.sh > /tmp/install.sh && bash /tmp/install.sh
dolt config --global --add user.email rimantas@keyspace.lt
dolt config --global --add user.name "rl1987"

pip3 install --upgrade requests lxml js2xml doltpy scrapy openpyxl pandas xlrd Scapy openai

curl -sSL https://repos.insights.digitalocean.com/install.sh -o /tmp/install.sh
bash /tmp/install.sh

mkdir /root/data

pushd /root/data || exit
dolt clone rl1987/paylesshealth
popd || exit

wget https://github.com/lc/gau/releases/download/v2.1.2/gau_2.1.2_linux_amd64.tar.gz -O /tmp/gau_2.1.2_linux_amd64.tar.gz
pushd /tmp || exit
tar xvf gau_2.1.2_linux_amd64.tar.gz
mv gau /usr/bin/gau
popd || exit

swapoff -a
dd if=/dev/zero of=/swapfile bs=1G count=16
chmod 0600 /swapfile
mkswap /swapfile
swapon /swapfile
echo "/swapfile swap swap sw 0 0" >> /etc/fstab

curl -fsSL https://deb.nodesource.com/setup_19.x -o /tmp/install_node.sh
bash /tmp/install_node.sh
apt-get install -y gcc g++ make nodejs

npm install crontab-ui -g
npm install pm2 -g

{
    echo "HOST=0.0.0.0"
    echo "PORT=9000"
    echo "BASIC_AUTH_USER=rl"
    echo "BASIC_AUTH_PWD=r29483tuy3490y30f98h"
    echo "ENABLE_AUTOSAVE=true"
} >> /etc/environment

export HOST=0.0.0.0
export PORT=9000
export BASIC_AUTH_USER=rl
export BASIC_AUTH_PWD=r29483tuy3490y30f98h
export ENABLE_AUTOSAVE=true

pm2 start crontab-ui -- --autosave
pm2 save
pm2 startup systemd
