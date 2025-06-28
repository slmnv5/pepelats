#!/bin/bash

# use this to install 3.5 inch LCD for raspberry pi
cd ~ || exit


# copy LCD screen driver, check if this is correct driver for your screen
sudo cp -fvn ./pepelats/config/script/mhs35.dtbo /boot/overlays/

THE_DIR="/boot/firmware"

# save original Raspbian config file #1
THE_FILE="config.txt"
THE_PATH="$THE_DIR/$THE_FILE"
sudo cp -vn $THE_PATH $THE_PATH.bak
# replace by custom file
sudo cp -fv ~/pepelats/config/script/$THE_FILE $THE_PATH

# save original Raspbian config file #2
THE_FILE="cmdline.txt"
THE_PATH="$THE_DIR/$THE_FILE"
sudo cp -vn $THE_PATH $THE_PATH.bak
# replace by custom file
sudo cp -fv ~/pepelats/config/script/$THE_FILE $THE_PATH

