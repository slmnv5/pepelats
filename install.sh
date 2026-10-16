#!/bin/bash

cd ~ || exit 1

D1=https://github.com/slmnv5/pepelats/releases/tag/latest

wget -N "$D1"/pepelats.zip || exit 1
unzip -o ~/pepelats.zip -d ~/pepe/ || exit 1

START_CMD=$(cat ~/.profile | grep "~/pepe/loop.sh")
if [ -z "$START_CMD" ]; then
  echo "" >> ~/.profile 
  echo 'if [ -z "$SSH_CONNECTION" ]; then ~/pepe/loop.sh; fi' >> ~/.profile
fi

echo "====== PEPELATS INSTALL SUCCESS =======" 

echo "install: wget -qO- "$D1"/install.sh | bash


