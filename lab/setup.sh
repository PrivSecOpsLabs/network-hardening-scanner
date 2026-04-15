#!/bin/bash
set -e

echo ">>> Configuring lab target with intentional misconfigurations..."

mkdir -p /var/run/sshd

sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
echo "MaxAuthTries 6" >> /etc/ssh/sshd_config
sed -i 's/#X11Forwarding.*/X11Forwarding yes/' /etc/ssh/sshd_config

echo "root:labpassword" | chpasswd

ufw disable || true

echo "ServerName localhost" >> /etc/apache2/apache2.conf

echo ">>> Lab target ready."
