## MIDI drum

MIDI drum sends MIDI messages to external drum machine to synchronize it with the looper, change drum volume, program,
etc. Translation of these MIDI messages may be done done with IOs app
MidiFire [midi_fire_scene.txt](./../config/etc/txt/midi_fire_scene.txt) Any IOs drum machine app may be
used.

MIDI messages sent are:

*1) [0xF0, 0x5A, BPM_LIST, 0xF7] - sysEx message sent after 1st loop recorded and BPM calculated. Use it to set BPM on
external drum. BPM_LIST is 6 bytes long. Examples:

* bpm=0123.45, BPM_LIST=[0, 1, 2, 3, 4, 5]
* bpm=0070.05, BPM_LIST=[0, 0, 7, 0, 0, 5]
* bpm=1201.33, BPM_LIST=[1. 2. 0, 1, 3, 3]

  *2) [0xF0, 0x5B, 0xF7] - sysEx message sent at start of each bar. Use it to synchronize external drum
  *3) [0xB0, 8, VOL] - set volume where VOL has value from 0 to 128.
  *4) [0xFC] - stop drum. There is no start message, instead 2) is used.
  *4) [0xC0, PROG] - program change where PROG number from 0 to 32.

### MIDI port

**Main.ini** configuration has section "MIDI" and option "midi_out". This is MIDI port name (or part of the full name)
that is used to send messages. If port is not available (device is not connected) so called "FakeMidiOut" port is used
which only logs few messages.
You can see MIDI ports in service menu.



