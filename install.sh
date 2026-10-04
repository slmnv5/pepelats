#!/bin/bash

cd ~ || exit 1
rm pepe.zip
wget -O pepe.zip  https://github.com/slmnv5/pepelats/raw/refs/heads/main/pepelats.zip || exit 1
unzip  -o ~/pepe.zip -d ~/pepe/ || exit 1

echo "" >> ~/.profile 
echo 'if [ -z "$SSH_CONNECTION" ]; then ~/pepe/loop.sh; fi' >> ~/.profile

# to call this install script: wget -qO-  https://github.com/slmnv5/pepelats/raw/refs/heads/main/install.sh | bash


