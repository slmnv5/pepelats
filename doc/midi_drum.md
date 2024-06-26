## MIDI drum

**MIDI drum** sends MIDI messages to external drum machine to synchronize it with the looper, change drum volume,
program,
etc. Translation of these MIDI messages may be done with IOS app
MidiFire [midi_fire_scene.txt](./../config/etc/txt/midi_fire_scene.txt) Any IOS drum machine app may be
used.

MIDI messages sent are:

*1) [0xF0, 0x5A, BPM_LIST, 0xF7] - sysEx message sent after 1st loop recorded and BPM calculated. Use it to set BPM on
external slave device. Here **BPM_LIST** is 6 bytes long. Examples:

* bpm=0070.05, BPM_LIST=[0, 0, 7, 0, 0, 5]
* bpm=1201.33, BPM_LIST=[1, 2, 0, 1, 3, 3]

*2) [0xF0, 0x5B, 0xF7] - sysEx message sent at start of each bar. Use it to synchronize external slave device.
*3) [0xB0, 8, VOL] - set volume where VOL has value from 0 to 127.
*4) [0xFC] - stop drum. There is no start message, instead 2) is used.
*5) [0xF0, 0x5C, 0xF7] - sysEx for program change, it may be ignored.
*6) [0xF0, 0x5D, 0xF7] - sysEx for drum fill or break, it may be ignored.

### MIDI out port

main.ini configuration has section "MIDI" and option "midi_out". This is MIDI port name (or part of the name)
that is used to send messages. If port is not available (device is not connected) so called "FakeMidiOut" port is used
which only logs few MIDI messages.
You can see MIDI ports in service menu.



