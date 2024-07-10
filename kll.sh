#!/bin/bash

sudo pkill looper.sh
sudo pkill python

export PYTHONPATH=~/pepelats/src/:~/pepelats/
python ./src/serv/server.py





