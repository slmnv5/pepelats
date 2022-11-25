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
export PEDAL_PORT_NAME='BlueBoard'
# Use this MIDI port as clock output
export CLOCK_PORT_NAME='Sshpadnew'

#check ALSA devices and use first one found
export USB_AUDIO_NAMES='VALETON GP,USB Audio'

THIS_DIR=$(dirname "$0")
cd "$THIS_DIR/src" || exit 1

found=$(pgrep --full start_looper.py)
if [ -n "$found" ]; then
  echo "Exiting, already running"
  exit 1
fi

CODE_OPTIMIZE="-O"
REDIRECT="2> $THIS_DIR/messages.txt"
SUDO=""
for var in "$@"; do
  if [ "$var" = "--debug" ] || [ "$var" = "--info"  ]; then
    CODE_OPTIMIZE=""
    REDIRECT=""
  fi
  if [ "$var" = "--kbd" ]; then
    SUDO="sudo"
  fi
done

PYTHON_CMD="$SUDO python $CODE_OPTIMIZE ./start_looper.py  $* $REDIRECT"
echo "$PYTHON_CMD"

# disable under voltage error on screen and disable typing echo
sudo dmesg -D
stty -echo

while true; do
  killall -s 9 -w -v python
  sleep 10
  $PYTHON_CMD
done

sudo dmesg -E
stty echo
