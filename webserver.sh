#!/bin/bash

sudo pkill looper.sh
sudo pkill webserver.sh
killall -9 -qw python > /dev/null

TMP=$(dirname "$0")
cd "$TMP" || exit 1

sudo dmesg -D
sudo setfont Uni1-VGA32x16
stty -echo

export PYTHONPATH=~/pepelats/src
python ./src/serv/webserver.py

sudo dmesg -E
sudo setfont Uni1-VGA16
stty echo

