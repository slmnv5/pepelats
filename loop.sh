#!/bin/bash

if pidof -o %PPID -x loop.sh > /dev/null; then
    echo "Process already running"
    exit 1
fi

cd "$(dirname "$0")" || exit 1

prepare_files () {
  local SAVE_SONG=~/save_song
  local LOG=loop.txt
  local BAK=loop.bak
  local INI=loop.ini

  mkdir "$SAVE_SONG" 2>/dev/null
  touch "$LOG" "$INI" "$BAK"
  cat "$LOG" >> "$BAK"
  chmod a+rw "$LOG $BAK $INI $SAVE_SONG/*" 2>/dev/null
  tail -n 1000 "$BAK" > "$LOG"
  mv "$LOG" "$BAK"
  echo "== $(date) ==" > "$LOG"
}

prepare_command() {
  # sudo required for keyboard input
  local SUDO=""
  # disable assert
  local CODE_OPTIMIZE="-O"
  local var
  for var in "$@"; do
    if [ "$var" = "--debug" ] || [ "$var" = "--info" ]; then
      CODE_OPTIMIZE=""
    fi
    if [ "$var" = "--kbd" ]; then
      SUDO="sudo -E"
    fi
  done
  if [ -f ./main.dist/main.bin ]; then
    PYTHON_CMD="$SUDO ./main.dist/main.bin $*"
  else
    PYTHON_CMD="$SUDO python $CODE_OPTIMIZE ./src/main.py $*"
  fi
}

prepare_files
prepare_command

# disable under voltage error on screen, set huge font size, disable typing echo
sudo dmesg -D
stty -echo
while true; do
  echo "===== new run ====="
  sudo pkill -9 python
  sleep 5
  $PYTHON_CMD
done
sudo dmesg -E
stty echo

