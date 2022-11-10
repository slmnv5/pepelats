#!/bin/bash

# commands to set and save ALSA mixer values
# works for TROND (and similar using C-media chip) USB audio

CARDN=$(aplay -l | grep -i -m1 "usb audio" | cut -f1 -d ':' | cut -f2 -d ' ')

if [[ "$CARDN" == "" ]]; then echo "USB audio not connected!"; exit 20; fi


amixer -c "$CARDN" set "Auto Gain Control" off
amixer -c "$CARDN" set Speaker on
amixer -c "$CARDN" set Speaker playback 90%
amixer -c "$CARDN" set Mic capture on
amixer -c "$CARDN" set Mic playback on
amixer -c "$CARDN" set Mic playback 90%
amixer -c "$CARDN" set Mic capture  35%

# save to /var/lib/alsa/asound.state
sudo alsactl store

