#!/bin/sh

# Options:
# --debug or --info - set level of logging
# --kbd - use keyboard for MIDI input (see KBD_NOTES)
# --count - count notes

export ENV_KBD_NOTES='"q": 12, "w": 13, "1":60, "2": 62, "3": 64, "4": 65'

# Looper parameters passed via environment
export ENV_MAX_LEN_SECONDS=60
export ENV_SD_RATE=44100

# Use this MIDI port as input
export ENV_MIDI_IN_PORT='BlueBoard'
# Use this MIDI port as clock output
export ENV_MIDI_OUT_PORT='Play mk3' # 'Sshpadnew'
# use this frame buffer if there are few, only Linux
ENV_FRAME_BUFFER_ID=1

#check ALSA devices and use first one found
export ENV_USB_AUDIO_NAMES='VALETON GP,USB Audio'

THIS_DIR=$(dirname "$0")
cd "$THIS_DIR/src" || exit 1

found=$(pgrep --full start_looper.py)
if [ -n "$found" ]; then
  echo "Exiting, already running"
  exit 1
fi

CODE_OPTIMIZE="-O"
SUDO=""
for var in "$@"; do
  if [ "$var" = "--debug" ] || [ "$var" = "--info" ]; then
    CODE_OPTIMIZE=""
  fi
  if [ "$var" = "--kbd" ]; then
    SUDO="sudo"
  fi
done

PYTHON_CMD="$SUDO python $CODE_OPTIMIZE ./start_looper.py  $*"
echo "$PYTHON_CMD"

# disable under voltage error on screen and disable typing echo
sudo dmesg -D
stty -echo

while true; do
  killall -s 9 -w -v python
  . "$THIS_DIR/.saved_env.sh"
  sleep 10
  $PYTHON_CMD
done

sudo dmesg -E
stty echo
