#!/bin/sh
# This script starts pepelats audio looper
# Options are:
# --debug or --info - level of logging
# --kbd - use keyboard for MIDI input (see KBD_NOTES)
# --count - count notes

export KBD_NOTES='"q": 12, "w": 13, "1":60, "2": 62, "3": 64, "4": 65'

# Looper parameters passed via environment
export MAX_LEN_SECONDS=60
export SD_RATE=44100

#killall -9 python
export PYTHONPATH="${PYTHONPATH}:$HOME/mypi_music/src:$HOME/mypi_music"

python ./drum/_mididrum.py

