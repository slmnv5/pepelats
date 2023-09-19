#!/bin/bash


sudo apt -y install python3-pip
sudo pip3 install sounddevice keyboard
sudo apt -y install python3-rtmidi python3-alsaaudio
sudo apt -y install libportaudio2


# make bif font
sudo sed -i 's/FONTFACE=""/FONTFACE="Terminus"/g' /etc/default/console-setup
sudo sed -i 's/FONTSIZE=""/FONTSIZE="16X32"/g' /etc/default/console-setup
