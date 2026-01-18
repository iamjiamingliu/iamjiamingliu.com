#!/bin/bash
set -e

cd /root/iamjiamingliu.com
git pull

source .venv/bin/activate

systemctl restart iamjiamingliu.com
