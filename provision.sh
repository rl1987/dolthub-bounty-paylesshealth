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
dolt clone rl1987/standard-charge-files
popd || exit

swapoff -a
dd if=/dev/zero of=/swapfile bs=1G count=16
chmod 0600 /swapfile
mkswap /swapfile
swapon /swapfile
echo "/swapfile swap swap sw 0 0" >> /etc/fstab
