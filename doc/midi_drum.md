## MIDI drum

**MIDI drum** sends MIDI sysEx messages to external drum machine to synchronize it with the looper, change drum volume,
program, etc. Processing of these custom MIDI messages need to be done with IOS application.   
As example here is script file for MidiFire [midi_fire_scene.txt](etc/txt/midi_fire_scene.txt) that controls drum
machine on IOS.

### MIDI messages sent are:

*1) [0xF0, 0x5A, BPM_LIST, 0xF7] - sysEx message sent after 1-st loop recorded and BPM calculated. Use it to set BPM on
external slave device. Here **BPM_LIST** is 6 bytes long. Examples:

* bpm=0070.05, BPM_LIST=[0, 0, 7, 0, 0, 5]
* bpm=1201.33, BPM_LIST=[1, 2, 0, 1, 3, 3]

*2) [0xF0, 0x5B, 0xF7] - sysEx message sent at start of each bar. Use it to synchronize external slave device.
*3) [0xB0, 8, VOL] - sent when drum volume changes, VOL has value from 0 to 127.
*4) [0xFC] - sent when drum stops. There is no start message, instead 2) must be used.
*5) [0xF0, 0x5C, 0xF7] - sysEx sent when drum is randomized. Implement it in slave device.
*6) [0xF0, 0x5D, 0xF7] - sysEx for drum fill or break. Implement it in slave device.

### MIDI out port for MIDI drum

**main.ini** configuration has section "MIDI" and option "midi_out". This is MIDI port name (or part of the name)
that is used to send MIDI drum messages. If port is not available (device is not connected) so called "FakeMidiOut" port
is used which only logs few MIDI messages.



