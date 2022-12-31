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

# Use this MIDI port as input
export MIDI_IN_PORT_NAME='BlueBoard'
# Use this MIDI port as clock output
export MIDI_OUT_PORT_NAME='Sshpadnew'

#check ALSA devices and use first one found
export USB_AUDIO_NAMES='VALETON GP,USB Audio'

export ENV_ROOT_DIR=$(dirname "$0")
cd "$ENV_ROOT_DIR/src" || exit 1

#killall -9 python
export PYTHONPATH="${PYTHONPATH}:$HOME/mypi_music/src:$HOME/mypi_music"

python ./drum/_mididrum.py

