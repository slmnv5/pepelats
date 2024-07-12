#!/bin/bash

sudo pkill looper.sh
killall -9 -qw python > /dev/null

TMP=$(dirname "$0")
cd "$TMP" || exit 1

sudo dmesg -D
sudo setfont Uni1-VGA32x16
stty -echo

export PYTHONPATH=~/pepelats/src/:~/pepelats/
python ./src/serv/server.py

sudo dmesg -E
sudo setfont Uni1-VGA16
stty echo

