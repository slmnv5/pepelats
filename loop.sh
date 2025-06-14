#!/bin/sh

if pidof -o %PPID -x "$(basename "$0")">/dev/null; then
    echo "Process already running"
    exit 1
fi
cd "$(dirname "$0")" || exit 1

SAVE_SONG=./../save_song
LOG=./../loop.log
BAK=./../loop.bak

mkdir "$SAVE_SONG" 2>/dev/null
touch "$LOG"
cat "$LOG" >> "$BAK"
chmod a+rw "$LOG $BAK $SAVE_SONG/*" 2>/dev/null
tail -n 1000 "$BAK" > "$LOG"
mv "$LOG" "$BAK"
echo "== $(date) ==" > "$LOG"

# sudo required for keyboard
SUDO=""
for var in "$@"; do
  if [ "$var" = "--kbd" ]; then
    SUDO="sudo -E"
  fi
done

# disable under voltage error on screen, set huge font size, disable typing echo
sudo dmesg -D
sudo setfont Uni1-VGA32x16
#stty -echo
while true; do
  cls
  echo "===== new run ====="
  killall -9 -qw python > /dev/null
  PYTHON_CMD="$SUDO ./main.dist/main.bin $*"
  $PYTHON_CMD
  if [ "$?" -ne "0" ]; then sleep 10; fi
done

#sudo dmesg -E
sudo setfont Uni1-VGA16
#stty echo

