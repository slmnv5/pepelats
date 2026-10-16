#!/bin/bash

cd ~ || exit 1
rm pepe.zip
wget pepe.zip  https://github.com/slmnv5/pepelats/raw/refs/heads/main/pepelats1.zip || exit 1
unzip -o ~/pepe.zip -d ~/pepe/ || exit 1

rm pepe.zip || exit 1
wget pepe.zip  https://github.com/slmnv5/pepelats/raw/refs/heads/main/pepelats2.zip || exit 1
unzip -o ~/pepe.zip -d ~/pepe/ || exit 1
rm pepe.zip || exit 1

START_CMD=$(cat ~/.profile | grep "~/pepe/loop.sh")
if [ -z "$START_CMD" ]; then
  echo "" >> ~/.profile 
  echo 'if [ -z "$SSH_CONNECTION" ]; then ~/pepe/loop.sh; fi' >> ~/.profile
fi

echo "====== PEPELATS INSTALL SUCCESS =======" 

# to call this install script: wget -qO-  https://github.com/slmnv5/pepelats/raw/refs/heads/main/install.sh | bash


