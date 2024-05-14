#!/bin/bash

cd ~ || exit

# non debian python packages
sudo apt -y install python3-pip
pip install sounddevice keyboard  --break-system-packages
# debian python packages
sudo apt -y install python3-rtmidi python3-alsaaudio python3-numpy
sudo apt -y install libportaudio2


sudo apt -y install git
# clone repository
git clone https://github.com/slmnv5/pepelats.git

# copy LCD screen driver, check if this is your driver
sudo cp -fvn ./pepelats/config/etc/scripts/mhs35.dtbo /boot/overlays/

# copy Raspbian config files
THE_FILE="config.txt"
THE_DIR="/boot/firmware"
THE_FULL="$THE_DIR/$THE_FILE"
sudo cp -vn $THE_FULL $THE_FULL.old
sudo cp -fv ./pepelats/config/etc/txt/$THE_FILE $THE_FULL

THE_FILE="cmdline.txt"
THE_DIR="/boot/firmware"
THE_FULL="$THE_DIR/$THE_FILE"
sudo cp -v $THE_FULL $THE_FULL.old
sudo cp -fv ./pepelats/config/etc/txt/$THE_FILE $THE_FULL

