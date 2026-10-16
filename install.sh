#!/bin/bash

cd ~ || exit 1
# only get if new file, else use existing file
wget -N https://github.com/slmnv5/pepelats/raw/refs/heads/main/pepelats1.zip || exit 1
unzip -o ~/pepelats1.zip -d ~/pepe/ || exit 1

wget -N https://github.com/slmnv5/pepelats/raw/refs/heads/main/pepelats2.zip || exit 1
unzip -o ~/pepelats2.zip -d ~/pepe/ || exit 1

START_CMD=$(cat ~/.profile | grep "~/pepe/loop.sh")
if [ -z "$START_CMD" ]; then
  echo "" >> ~/.profile 
  echo 'if [ -z "$SSH_CONNECTION" ]; then ~/pepe/loop.sh; fi' >> ~/.profile
fi

echo "====== PEPELATS INSTALL SUCCESS =======" 

# to call this install script: wget -qO-  https://github.com/slmnv5/pepelats/raw/refs/heads/main/install.sh | bash
