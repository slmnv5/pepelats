#!/bin/sh

  # sudo required for keyboard
  SUDO=""
  export HAS_KBD=""
  export MIDI_IN=""
  export LOCAL_IP=""

test_all() {
  # sudo required for keyboard
  SUDO=""
  HAS_KBD=""
  MIDI_IN=""
  LOCAL_IP=$(ip route | sed -E  "s/^.* src ([^ ]+).*/\1/" | head -1)

  if lsusb | grep -i "USB Keyboard"; then HAS_KBD="YES"; SUDO="sudo -E"; fi
  if aconnect -i | grep "^client " | grep -v "type=kernel"; then MIDI_IN="YES"; fi
}

TMP=$(dirname "$0")
cd "$TMP" || exit 1

if pidof -o %PPID -x "looper.sh">/dev/null; then
    echo "Process already running"
    exit 1
fi

sudo chmod a+rw ./save_song/*
touch local.ini log.txt log.bak
chmod a+rw log.txt log.bak
cat log.txt >> log.bak
tail -n 1000 log.bak > log.txt
mv log.txt log.bak
echo "== $(date) ==" > log.txt

# disable under voltage error on screen, set huge font size, disable typing echo
sudo dmesg -D
sudo setfont Uni1-VGA32x16
stty -echo

while true; do
  test_all
  if [ -z $HAS_KBD ] && [ -z $MIDI_IN ]; then
    echo "Connect computer keyboard or MIDI input device"
    sleep 5
    continue
  fi
  msg="LOCAL_IP = $LOCAL_IP; HAS_KBD = $HAS_KBD; MIDI_IN = $MIDI_IN;"
  echo "$msg" >> log.txt
  echo "$msg"
  killall -9 -qw python > /dev/null

  PYTHON_CMD="$SUDO ./main.dist/main.bin $*"
  echo "$PYTHON_CMD"
  $PYTHON_CMD
  sleep 5
done

sudo dmesg -E
sudo setfont Uni1-VGA16
stty echo
