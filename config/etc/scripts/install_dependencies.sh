#!/bin/bash

cd ~ || exit

# non debian python packages
sudo apt -y install python3-pip
pip install sounddevice keyboard  --break-system-packages
# debian python packages
sudo apt -y install python3-rtmidi python3-alsaaudio python3-numpy
sudo apt -y install libportaudio2

sudo apt -y install git
# clone this repository
git clone https://github.com/slmnv5/pepelats.git

# copy LCD screen driver, check if this is correct driver for your screen
sudo cp -fvn ./pepelats/config/etc/scripts/mhs35.dtbo /boot/overlays/

# save original Raspbian config file #1
THE_FILE="config.txt"
THE_DIR="/boot/firmware"
THE_PATH="$THE_DIR/$THE_FILE"
sudo cp -vn $THE_PATH $THE_PATH.old
# replace by custom file
sudo cp -fv ./pepelats/config/etc/txt/$THE_FILE $THE_PATH

# save original Raspbian config file #2
THE_FILE="cmdline.txt"
THE_DIR="/boot/firmware"
THE_PATH="$THE_DIR/$THE_FILE"
sudo cp -vn $THE_PATH $THE_PATH.old
# replace by custom file
sudo cp -fv ./pepelats/config/etc/txt/$THE_FILE $THE_PATH

