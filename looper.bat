:: This script starts pepelats audio looper
:: Options are:
:: --debug or --info - level of logging
:: --kbd - use keyboard for MIDI input (see KBD_NOTES)
:: --count - count notes

set "KBD_NOTES="1":60, "2": 62, "3": 64, "4": 65, "q": 12, "w": 13"

::Looper parameters passed via env.
set MAX_LEN_SECONDS=60
set SD_RATE=44100

::Use this MIDI port as input
set PEDAL_PORT_NAME='BlueBoard'

::Check ALSA devices and use first one found
set USB_AUDIO_NAMES='VALETON GP,USB Audio'

set THIS_DIR=%~dp0
cd "%THIS_DIR%" || goto stop

::exit if already running, search for cmd window title
title no_title
tasklist /v /fo csv | find "start_looper_cmd" && goto stop


:loop
title start_looper_cmd
taskkill /F /IM python.exe
python.exe ./start_looper.py %*
timeout 10
goto loop

title no_title

:stop


